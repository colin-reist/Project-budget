from decimal import Decimal
from datetime import date, timedelta

from django.db.models import Sum, Q
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Budget, SavingsGoal
from .serializers import BudgetSerializer, BudgetListSerializer, SavingsGoalSerializer, SavingsGoalListSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les budgets
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['period', 'category', 'is_active']
    search_fields = ['name']
    ordering_fields = ['created_at', 'amount', 'start_date']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Retourne uniquement les budgets de l'utilisateur connecté
        """
        return Budget.objects.filter(user=self.request.user).select_related(
            'category'
        )

    def get_serializer_class(self):
        """
        Utilise un serializer différent pour la liste
        """
        if self.action == 'list':
            return BudgetListSerializer
        return BudgetSerializer

    def get_serializer_context(self):
        """
        Ajoute year/month au contexte pour permettre le calcul historique des dépenses.
        """
        context = super().get_serializer_context()
        today = date.today()
        try:
            year = int(self.request.query_params.get('year', today.year))
            month = int(self.request.query_params.get('month', today.month))
        except (ValueError, TypeError):
            year, month = today.year, today.month
        context['year'] = year
        context['month'] = month
        return context

    def perform_create(self, serializer):
        """
        Associe automatiquement l'utilisateur connecté au budget
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Retourne un résumé des budgets actifs pour le mois sélectionné.
        """
        today = date.today()
        try:
            year = int(request.query_params.get('year', today.year))
            month = int(request.query_params.get('month', today.month))
        except (ValueError, TypeError):
            year, month = today.year, today.month

        budgets = list(self.get_queryset().filter(is_active=True))

        total_budgets = len(budgets)
        total_amount = Decimal('0.00')
        total_spent = Decimal('0.00')
        over_budget_count = 0
        alert_count = 0

        for b in budgets:
            spent = b.get_spent_amount_for_period(year, month)
            total_amount += b.amount
            total_spent += spent
            if spent > b.amount:
                over_budget_count += 1
            elif b.amount > 0 and float(spent / b.amount * 100) >= b.alert_threshold:
                alert_count += 1

        return Response({
            'total_budgets': total_budgets,
            'total_amount': total_amount,
            'total_spent': total_spent,
            'total_remaining': total_amount - total_spent,
            'over_budget_count': over_budget_count,
            'alert_count': alert_count,
            'percentage_used': round((total_spent / total_amount * 100) if total_amount > 0 else 0, 2)
        })

    @action(detail=False, methods=['get'])
    def dashboard_data(self, request):
        """
        Données budget vs réel pour le dashboard.
        Pour chaque budget actif mensuel : prévu, réel, écart.
        Inclut les catégories avec dépenses mais sans budget.
        """
        from transactions.models import Transaction
        from authentication.models import UserProfile

        user = request.user
        today = date.today()

        # Bornes du mois sélectionné (ou mois en cours par défaut)
        try:
            year = int(request.query_params.get('year', today.year))
            month = int(request.query_params.get('month', today.month))
        except (ValueError, TypeError):
            year, month = today.year, today.month

        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)

        # Budgets actifs mensuels (hors objectifs épargne ciblée)
        # Inclut les budgets normaux ET l'épargne obligatoire
        budgets = Budget.objects.filter(
            user=user, is_active=True, period='monthly'
        ).filter(
            Q(is_savings_goal=False) | Q(is_mandatory_savings=True)
        ).select_related('category')

        # Revenu mensuel du profil
        try:
            profile = UserProfile.objects.get(user=user)
            monthly_income = profile.monthly_income
        except UserProfile.DoesNotExist:
            monthly_income = Decimal('0.00')

        # Données par catégorie
        categories_data = []
        budgeted_category_ids = set()
        total_budget = Decimal('0.00')
        total_actual = Decimal('0.00')

        from accounts.models import Account as BudgetAccount
        cap = min(end, today) if (year, month) >= (today.year, today.month) else end

        for budget in budgets:
            # Calculer le montant dépensé pour le mois sélectionné (pas le mois courant)
            if budget.is_savings_goal or budget.is_mandatory_savings:
                savings_accounts = BudgetAccount.objects.filter(
                    user=user, account_type='savings', is_active=True
                )
                spent = (
                    Transaction.objects.filter(
                        user=user, type='transfer',
                        destination_account__in=savings_accounts,
                        date__gte=start, date__lte=cap
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                )
            else:
                spent = (
                    Transaction.objects.filter(
                        user=user, category=budget.category,
                        type='expense', date__gte=start, date__lte=cap
                    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                )

            total_budget += budget.amount
            total_actual += spent

            # Gérer épargne obligatoire (sans catégorie)
            if budget.is_mandatory_savings:
                categories_data.append({
                    'category_id': None,
                    'category_name': budget.name,
                    'category_color': 'green',
                    'category_icon': 'i-heroicons-banknotes',
                    'prevu': float(budget.amount),
                    'reel': float(spent),
                    'ecart': float(budget.amount - spent),
                    'is_over': spent > budget.amount,
                    'unbudgeted': False,
                    'is_mandatory_savings': True,
                })
            elif budget.category:
                # Budget normal avec catégorie
                budgeted_category_ids.add(budget.category_id)
                categories_data.append({
                    'category_id': budget.category_id,
                    'category_name': budget.category.name,
                    'category_color': budget.category.color,
                    'category_icon': budget.category.icon,
                    'prevu': float(budget.amount),
                    'reel': float(spent),
                    'ecart': float(budget.amount - spent),
                    'is_over': spent > budget.amount,
                    'unbudgeted': False,
                    'is_mandatory_savings': False,
                })

        # Catégories avec dépenses mais sans budget
        unbudgeted = (
            Transaction.objects.filter(
                user=user, type='expense',
                date__gte=start, date__lte=cap
            )
            .exclude(category_id__in=budgeted_category_ids)
            .exclude(category__isnull=True)
            .values('category__id', 'category__name', 'category__color', 'category__icon')
            .annotate(total=Sum('amount'))
        )

        for item in unbudgeted:
            amt = item['total'] or Decimal('0.00')
            total_actual += amt
            categories_data.append({
                'category_id': item['category__id'],
                'category_name': item['category__name'] or 'Sans catégorie',
                'category_color': item['category__color'] or 'gray',
                'category_icon': item['category__icon'] or 'i-heroicons-tag',
                'prevu': 0,
                'reel': float(amt),
                'ecart': float(-amt),
                'is_over': True,
                'unbudgeted': True,
            })

        # Revenus réels du mois
        actual_income = (
            Transaction.objects.filter(
                user=user, type='income',
                date__gte=start, date__lte=cap
            )
            .aggregate(total=Sum('amount'))['total']
            or Decimal('0.00')
        )

        return Response({
            'categories': categories_data,
            'solde_previsionnel': float(monthly_income - total_budget),
            'solde_reel': float(actual_income - total_actual),
            'ecart': float((actual_income - total_actual) - (monthly_income - total_budget)),
            'revenu_mensuel': float(monthly_income),
            'revenu_reel': float(actual_income),
            'total_budget': float(total_budget),
            'total_actual': float(total_actual),
        })

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Active/désactive un budget
        """
        budget = self.get_object()
        budget.is_active = not budget.is_active
        budget.save()
        serializer = self.get_serializer(budget)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def reset_all(self, request):
        """
        Supprime toutes les enveloppes (budgets) de l'utilisateur.

        DELETE /api/v1/budgets/reset_all/
        """
        deleted_count, _ = Budget.objects.filter(user=request.user).delete()
        return Response({'deleted': deleted_count})


class SavingsGoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les objectifs d'épargne
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['label']
    ordering_fields = ['created_at', 'target_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return SavingsGoalListSerializer
        return SavingsGoalSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def create_budget(self, request, pk=None):
        """
        Crée automatiquement un budget lié à cet objectif d'épargne.
        """
        from rest_framework import status as http_status

        goal = self.get_object()
        serializer = self.get_serializer(goal)
        calc = serializer.data.get('calculated_result') or {}

        # Déterminer le montant d'épargne
        if goal.saving_amount:
            amount = goal.saving_amount
        elif calc.get('saving_amount'):
            amount = Decimal(str(calc['saving_amount']))
        else:
            return Response(
                {'error': "Impossible de déterminer le montant d'épargne."},
                status=http_status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        # Mapper la fréquence vers la période Budget
        freq_to_period = {
            'daily': 'weekly',    # Pas de daily dans Budget, fallback weekly
            'weekly': 'weekly',
            'monthly': 'monthly',
            'yearly': 'yearly',
        }

        budget = Budget.objects.create(
            user=request.user,
            name=f'Épargne: {goal.label}',
            amount=amount,
            period=freq_to_period.get(goal.saving_frequency, 'monthly'),
            start_date=date.today(),
            end_date=goal.target_date,
            is_active=True,
            is_savings_goal=True,
            savings_goal=goal,
        )

        return Response({
            'budget_id': budget.id,
            'budget_name': budget.name,
            'amount': float(budget.amount),
            'message': f'Budget "{budget.name}" créé avec succès.'
        }, status=http_status.HTTP_201_CREATED)
