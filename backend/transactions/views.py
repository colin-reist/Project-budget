from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from .models import Transaction
from .serializers import TransactionSerializer, TransactionListSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les transactions
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'account', 'category', 'date', 'is_recurring']
    search_fields = ['description', 'notes']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']

    def get_queryset(self):
        """
        Retourne uniquement les transactions de l'utilisateur connecté
        """
        return Transaction.objects.filter(user=self.request.user).select_related(
            'account', 'category', 'destination_account'
        )

    def get_serializer_class(self):
        """
        Utilise un serializer différent pour la liste
        """
        if self.action == 'list':
            return TransactionListSerializer
        return TransactionSerializer

    def perform_create(self, serializer):
        """
        Associe automatiquement l'utilisateur connecté à la transaction
        """
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Lors d'une mise à jour via le web, si la transaction était ios_uncategorized
        et qu'une catégorie est maintenant assignée, on met à jour la source à 'web'
        afin d'indiquer que la transaction a été corrigée par l'utilisateur.
        La source est un champ read_only dans le serializer, il faut donc passer
        la nouvelle valeur directement via save().
        """
        instance = self.get_object()
        new_source = instance.source

        # Upgrade source from ios_uncategorized to web once the user
        # has corrected/categorized the transaction through the web UI.
        if instance.source == 'ios_uncategorized':
            # Check if a category is being assigned in this request
            incoming_category = serializer.validated_data.get('category', None)
            # Use the existing category if not being changed
            effective_category = incoming_category if 'category' in serializer.validated_data else instance.category
            if effective_category is not None:
                new_source = 'web'

        serializer.save(source=new_source)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Retourne des statistiques sur les transactions (excluant les transactions futures)
        Inclut aussi les montants des transactions futures jusqu'à la fin de la période
        """
        from datetime import date
        # Filtres de date
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = self.get_queryset()

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Transactions actuelles (jusqu'à aujourd'hui)
        # Exclure les ajustements des statistiques
        current_queryset = queryset.filter(date__lte=date.today()).exclude(type='adjustment')

        # Calcul des totaux par type pour les transactions actuelles
        stats = current_queryset.values('type').annotate(
            total=Sum('amount'),
            count=Count('id')
        )

        # Organiser les résultats
        result = {
            'income': {'total': 0, 'count': 0, 'future': 0},
            'expense': {'total': 0, 'count': 0, 'future': 0},
            'transfer': {'total': 0, 'count': 0, 'future': 0},
        }

        for stat in stats:
            result[stat['type']] = {
                'total': float(stat['total']),
                'count': stat['count'],
                'future': 0
            }

        # Calcul des transactions futures (après aujourd'hui jusqu'à la fin de la période)
        # Exclure les ajustements des statistiques
        future_queryset = queryset.filter(date__gt=date.today()).exclude(type='adjustment')
        future_stats = future_queryset.values('type').annotate(
            total=Sum('amount'),
            count=Count('id')
        )

        for stat in future_stats:
            if stat['type'] in result:
                result[stat['type']]['future'] = float(stat['total'])

        # Calcul du solde net
        result['net'] = result['income']['total'] - result['expense']['total']

        return Response(result)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Retourne les dépenses/revenus par catégorie (excluant les transactions futures)
        """
        from datetime import date
        transaction_type = request.query_params.get('type', 'expense')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = self.get_queryset().filter(type=transaction_type)

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Exclure les transactions futures et les ajustements par défaut
        queryset = queryset.filter(date__lte=date.today()).exclude(type='adjustment')

        # Grouper par catégorie
        stats = queryset.values(
            'category__id',
            'category__name',
            'category__color'
        ).annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')

        result = [
            {
                'category_id': stat['category__id'],
                'category_name': stat['category__name'] or 'Sans catégorie',
                'color': stat['category__color'] or 'gray',
                'total': float(stat['total']),
                'count': stat['count']
            }
            for stat in stats
        ]

        return Response(result)

    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """
        Retourne un résumé mensuel des transactions (excluant les transactions futures)
        """
        from datetime import date as date_class
        year = request.query_params.get('year', datetime.now().year)

        queryset = self.get_queryset().filter(date__year=year)

        # Exclure les transactions futures et les ajustements par défaut
        queryset = queryset.filter(date__lte=date_class.today()).exclude(type='adjustment')

        # Grouper par mois et type
        months_data = {}

        for month in range(1, 13):
            month_transactions = queryset.filter(date__month=month)

            income = month_transactions.filter(type='income').aggregate(
                total=Sum('amount')
            )['total'] or 0

            expense = month_transactions.filter(type='expense').aggregate(
                total=Sum('amount')
            )['total'] or 0

            months_data[month] = {
                'month': month,
                'income': float(income),
                'expense': float(expense),
                'net': float(income - expense)
            }

        return Response(months_data)
