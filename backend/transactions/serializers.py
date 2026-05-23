from rest_framework import serializers
from .models import Transaction
from accounts.serializers import AccountListSerializer
from categories.serializers import CategoryListSerializer


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Transaction
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    account_details = AccountListSerializer(source='account', read_only=True)
    category_details = CategoryListSerializer(source='category', read_only=True)
    destination_account_details = AccountListSerializer(source='destination_account', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'user',
            'account',
            'account_details',
            'category',
            'category_details',
            'type',
            'type_display',
            'amount',
            'description',
            'date',
            'notes',
            'destination_account',
            'destination_account_details',
            'is_recurring',
            'recurrence_frequency',
            'recurrence_interval',
            'recurrence_end_date',
            'recurring_series_id',
            'is_series_template',
            'source',
            'source_display',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'type_display', 'source_display',
            'source', 'account_details', 'category_details', 'destination_account_details',
            # Ces champs sont gérés automatiquement par la logique de génération
            'recurring_series_id', 'is_series_template',
        ]

    def validate(self, data):
        """
        Validation des données de la transaction
        """
        # Vérifier que le compte appartient à l'utilisateur
        if 'account' in data:
            if data['account'].user != self.context['request'].user:
                raise serializers.ValidationError({"account": "Ce compte ne vous appartient pas."})

        # Vérifier le compte destination pour les transferts
        if data.get('type') == 'transfer':
            if not data.get('destination_account'):
                raise serializers.ValidationError(
                    {"destination_account": "Un compte destination est requis pour un transfert."}
                )
            if data['destination_account'].user != self.context['request'].user:
                raise serializers.ValidationError(
                    {"destination_account": "Ce compte ne vous appartient pas."}
                )
            if data['account'] == data['destination_account']:
                raise serializers.ValidationError(
                    {"destination_account": "Le compte source et destination doivent être différents."}
                )

        # Vérifier que la catégorie correspond au type
        # Pour un PATCH, utiliser le type existant si non fourni
        if data.get('category'):
            transaction_type = data.get('type')
            if transaction_type is None and self.instance:
                transaction_type = self.instance.type

            if transaction_type in ['income', 'expense']:
                if data['category'].type != transaction_type:
                    raise serializers.ValidationError(
                        {"category": f"La catégorie doit être de type {transaction_type}."}
                    )

        return data


class TransactionListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des transactions
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id',
            'account',
            'account_name',
            'category',
            'category_name',
            'type',
            'type_display',
            'amount',
            'description',
            'date',
            'is_recurring',
            'recurring_series_id',
            'is_series_template',
            'source',
        ]
