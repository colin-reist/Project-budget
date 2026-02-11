from decimal import Decimal
from datetime import date, timedelta

from django.db.models import Sum
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

    def perform_create(self, serializer):
        """
        Associe automatiquement l'utilisateur connecté au budget
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Retourne un résumé des budgets actifs
        """
        budgets = self.get_queryset().filter(is_active=True)

        total_budgets = budgets.count()
        total_amount = sum(float(b.amount) for b in budgets)
        total_spent = sum(float(b.get_spent_amount()) for b in budgets)
        over_budget_count = sum(1 for b in budgets if b.is_over_budget())
        alert_count = sum(1 for b in budgets if b.is_alert_triggered() and not b.is_over_budget())

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

        # Bornes du mois en cours
        start = date(today.year, today.month, 1)
        if today.month == 12:
            end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(today.year, today.month + 1, 1) - timedelta(days=1)

        # Budgets actifs mensuels (hors objectifs épargne)
        budgets = Budget.objects.filter(
            user=user, is_active=True, period='monthly', is_savings_goal=False
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

        for budget in budgets:
            if not budget.category:
                continue
            budgeted_category_ids.add(budget.category_id)
            spent = budget.get_spent_amount()
            total_budget += budget.amount
            total_actual += spent

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
            })

        # Catégories avec dépenses mais sans budget
        unbudgeted = (
            Transaction.objects.filter(
                user=user, type='expense',
                date__gte=start, date__lte=min(end, today)
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
                date__gte=start, date__lte=min(end, today)
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
