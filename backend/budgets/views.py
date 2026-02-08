from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Budget
from .serializers import BudgetSerializer, BudgetListSerializer


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
