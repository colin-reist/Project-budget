import uuid
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models import Sum, Count, Min
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
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
        Supporte les filtres start_date / end_date en query params
        """
        queryset = Transaction.objects.filter(user=self.request.user).select_related(
            'account', 'category', 'destination_account'
        )
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset

    def get_serializer_class(self):
        """
        Utilise un serializer différent pour la liste
        """
        if self.action == 'list':
            return TransactionListSerializer
        return TransactionSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Force partial=True pour les mises à jour PATCH et PUT
        (certains proxies transforment PATCH en PUT)
        """
        if self.request and self.request.method in ['PATCH', 'PUT'] and self.action in ['update', 'partial_update']:
            kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)

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

    @action(detail=False, methods=['post'])
    def generate_recurring(self, request):
        """
        Génère les occurrences manquantes des transactions récurrentes jusqu'à aujourd'hui.

        Logique de liaison en série :
        - Si un template n'a pas encore de recurring_series_id, on lui en génère un et
          on marque is_series_template=True.
        - Les instances créées reçoivent le même recurring_series_id (is_series_template=False).
        - Les templates sont identifiés par is_series_template=True. Pour la compatibilité
          ascendante, on traite aussi les transactions is_recurring=True sans recurring_series_id.
        """
        today = date.today()
        created_count = 0

        # On considère comme templates toutes les transactions récurrentes ayant une fréquence.
        # Les instances non-templates sont exclues via is_series_template=False pour éviter
        # les doublons de génération (elles ont is_recurring=True mais ne sont pas des maîtres).
        recurring = self.get_queryset().filter(
            is_recurring=True,
            recurrence_frequency__isnull=False,
        ).filter(
            # Template explicite OU transaction récurrente sans série assignée (compatibilité)
            models.Q(is_series_template=True) | models.Q(recurring_series_id__isnull=True)
        )

        freq_map = {
            'daily': lambda d, i: d + timedelta(days=i),
            'weekly': lambda d, i: d + timedelta(weeks=i),
            'monthly': lambda d, i: d + relativedelta(months=i),
            'yearly': lambda d, i: d + relativedelta(years=i),
        }

        for transaction in recurring:
            freq = transaction.recurrence_frequency
            interval = transaction.recurrence_interval or 1
            advance = freq_map.get(freq)
            if not advance:
                continue

            # Assigner un UUID de série si le template n'en a pas encore
            if not transaction.recurring_series_id:
                series_id = uuid.uuid4()
                Transaction.objects.filter(pk=transaction.pk).update(
                    recurring_series_id=series_id,
                    is_series_template=True,
                )
                transaction.recurring_series_id = series_id
                transaction.is_series_template = True

                # Rétroactivement lier les instances existantes qui correspondent
                # à cette série (même description + compte + montant + type)
                Transaction.objects.filter(
                    user=request.user,
                    description=transaction.description,
                    account=transaction.account,
                    amount=transaction.amount,
                    type=transaction.type,
                    is_recurring=True,
                    recurring_series_id__isnull=True,
                    is_series_template=False,
                ).exclude(pk=transaction.pk).update(
                    recurring_series_id=series_id,
                )

            series_id = transaction.recurring_series_id
            end = transaction.recurrence_end_date if transaction.recurrence_end_date else today + timedelta(days=365)
            current = transaction.date

            # Boucle de la date de base jusqu'à la fin de la récurrence
            while current <= end:
                # Ne pas créer une occurrence pour la date de base (= le template lui-même)
                if current > transaction.date:
                    exists = Transaction.objects.filter(
                        user=request.user,
                        recurring_series_id=series_id,
                        date=current,
                    ).exists()

                    # Fallback pour les instances sans series_id mais mêmes attributs
                    if not exists:
                        exists = Transaction.objects.filter(
                            user=request.user,
                            description=transaction.description,
                            account=transaction.account,
                            amount=transaction.amount,
                            type=transaction.type,
                            date=current,
                        ).exists()

                    if not exists:
                        Transaction.objects.create(
                            user=request.user,
                            account=transaction.account,
                            category=transaction.category,
                            destination_account=transaction.destination_account,
                            type=transaction.type,
                            amount=transaction.amount,
                            description=transaction.description,
                            date=current,
                            notes=transaction.notes,
                            is_recurring=True,
                            recurrence_frequency=transaction.recurrence_frequency,
                            recurrence_interval=transaction.recurrence_interval,
                            recurrence_end_date=transaction.recurrence_end_date,
                            recurring_series_id=series_id,
                            is_series_template=False,
                            source='web',
                        )
                        created_count += 1

                current = advance(current, interval)

        return Response({'created': created_count})

    @action(detail=False, methods=['get'])
    def recurring_series(self, request):
        """
        Liste toutes les séries récurrentes de l'utilisateur.

        Retourne uniquement les templates (is_series_template=True ou transactions récurrentes
        sans série assignée pour la compatibilité ascendante), enrichis de :
        - next_occurrence : prochaine date future parmi les instances
        - total_instances : nombre total d'instances générées (hors template)
        """
        today = date.today()

        templates = self.get_queryset().filter(
            is_recurring=True,
            recurrence_frequency__isnull=False,
        ).filter(
            models.Q(is_series_template=True) | models.Q(recurring_series_id__isnull=True)
        ).select_related('account', 'category')

        result = []
        for t in templates:
            # Calculer la prochaine occurrence et le nombre d'instances liées à la série
            if t.recurring_series_id:
                instances_qs = Transaction.objects.filter(
                    user=request.user,
                    recurring_series_id=t.recurring_series_id,
                    is_series_template=False,
                )
            else:
                # Compatibilité : séries non encore migrées, lookup par attributs
                instances_qs = Transaction.objects.filter(
                    user=request.user,
                    description=t.description,
                    account=t.account,
                    amount=t.amount,
                    type=t.type,
                    is_recurring=True,
                ).exclude(pk=t.pk)

            total_instances = instances_qs.count()

            # Prochaine occurrence : date future minimale parmi toutes les instances + template
            future_qs = instances_qs.filter(date__gt=today).order_by('date')
            next_instance = future_qs.first()
            next_occurrence = next_instance.date.isoformat() if next_instance else None

            # Si le template lui-même est dans le futur et qu'on n'a pas de next_occurrence
            if not next_occurrence and t.date > today:
                next_occurrence = t.date.isoformat()

            result.append({
                'id': t.id,
                'description': t.description,
                'amount': str(t.amount),
                'type': t.type,
                'recurrence_frequency': t.recurrence_frequency,
                'recurrence_interval': t.recurrence_interval,
                'recurrence_end_date': t.recurrence_end_date.isoformat() if t.recurrence_end_date else None,
                'account': {
                    'id': t.account.id,
                    'name': t.account.name,
                    'currency': t.account.currency,
                },
                'category': {
                    'id': t.category.id,
                    'name': t.category.name,
                    'color': t.category.color,
                    'icon': t.category.icon,
                } if t.category else None,
                'next_occurrence': next_occurrence,
                'total_instances': total_instances,
                'recurring_series_id': str(t.recurring_series_id) if t.recurring_series_id else None,
            })

        # Tri : séries avec prochaine occurrence en premier
        result.sort(key=lambda x: (x['next_occurrence'] is None, x['next_occurrence'] or ''))

        return Response(result)

    @action(detail=True, methods=['post'])
    def update_series(self, request, pk=None):
        """
        Met à jour toutes les instances FUTURES d'une série récurrente.

        Paramètres du body :
        - from_date (optionnel, str ISO) : ne modifier qu'à partir de cette date (incluse)
        - amount, description, category, account, notes, recurrence_end_date, etc.

        Si from_date n'est pas fourni, toutes les instances futures (>= aujourd'hui) sont mises à jour.
        Le template lui-même est aussi mis à jour si from_date n'est pas fourni ou correspond à sa date.
        """
        today = date.today()
        template = self.get_object()

        if not template.recurring_series_id:
            return Response(
                {'error': 'Cette transaction ne fait pas partie d\'une série identifiée.'},
                status=400
            )

        from_date_str = request.data.get('from_date')
        try:
            from_date = date.fromisoformat(from_date_str) if from_date_str else today
        except (ValueError, TypeError):
            return Response({'error': 'from_date invalide, format attendu : YYYY-MM-DD'}, status=400)

        # Champs modifiables sur les instances
        allowed_fields = {
            'amount', 'description', 'category_id', 'notes',
            'recurrence_end_date', 'account_id',
        }

        # Construire le dict de mise à jour à partir des données validées
        update_data = {}
        raw = request.data

        if 'amount' in raw:
            update_data['amount'] = raw['amount']
        if 'description' in raw:
            update_data['description'] = raw['description']
        if 'category' in raw:
            update_data['category_id'] = raw['category'] if raw['category'] else None
        if 'notes' in raw:
            update_data['notes'] = raw['notes']
        if 'recurrence_end_date' in raw:
            update_data['recurrence_end_date'] = raw['recurrence_end_date'] if raw['recurrence_end_date'] else None
        if 'account' in raw:
            update_data['account_id'] = raw['account']

        if not update_data:
            return Response({'error': 'Aucun champ à mettre à jour fourni.'}, status=400)

        # Mettre à jour les instances futures
        updated = Transaction.objects.filter(
            user=request.user,
            recurring_series_id=template.recurring_series_id,
            is_series_template=False,
            date__gte=from_date,
        ).update(**update_data)

        # Mettre à jour le template lui-même si from_date <= date du template
        if from_date <= template.date:
            for field, value in update_data.items():
                setattr(template, field, value)
            template.save(update_fields=list(update_data.keys()))

        return Response({'updated': updated})

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

    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """
        Supprime toutes les transactions selon des filtres de date.
        DELETE /api/v1/transactions/bulk_delete/?start_date=2026-01-01&end_date=2026-12-31
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = self.get_queryset()

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        count, _ = queryset.delete()
        return Response({'deleted': count}, status=204)