from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Account
from .serializers import AccountSerializer, AccountListSerializer


class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les comptes bancaires
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_type', 'currency', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'balance', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Retourne uniquement les comptes de l'utilisateur connecté
        """
        return Account.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Utilise un serializer différent pour la liste
        """
        if self.action == 'list':
            return AccountListSerializer
        return AccountSerializer

    def perform_create(self, serializer):
        """
        Associe automatiquement l'utilisateur connecté au compte
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Retourne un résumé des comptes (total par devise, excluant les transactions futures)
        """
        accounts = self.get_queryset().filter(is_active=True)

        summary = {}
        for account in accounts:
            currency = account.currency
            if currency not in summary:
                summary[currency] = {
                    'total': 0,
                    'count': 0,
                    'by_type': {}
                }

            summary[currency]['total'] += float(account.get_current_balance())
            summary[currency]['count'] += 1

            account_type = account.get_account_type_display()
            if account_type not in summary[currency]['by_type']:
                summary[currency]['by_type'][account_type] = 0
            summary[currency]['by_type'][account_type] += float(account.get_current_balance())

        return Response(summary)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Active/désactive un compte
        """
        account = self.get_object()
        account.is_active = not account.is_active
        account.save()

        serializer = self.get_serializer(account)
        return Response(serializer.data)
