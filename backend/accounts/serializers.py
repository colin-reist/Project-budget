from rest_framework import serializers
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Account
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    current_balance = serializers.SerializerMethodField()
    projected_balance = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            'id',
            'user',
            'name',
            'account_type',
            'account_type_display',
            'balance',
            'current_balance',
            'projected_balance',
            'currency',
            'description',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'account_type_display', 'current_balance', 'projected_balance']

    def get_current_balance(self, obj):
        """Solde actuel (excluant les transactions futures)"""
        return float(obj.get_current_balance())

    def get_projected_balance(self, obj):
        """Solde projeté (incluant les transactions futures)"""
        return float(obj.get_projected_balance())

    def validate_balance(self, value):
        """
        Validation du solde
        """
        # Vérifier que le solde n'est pas négatif pour certains types de comptes
        account_type = self.instance.account_type if self.instance else self.initial_data.get('account_type')
        if value < 0 and account_type not in ['credit_card', 'loan']:
            raise serializers.ValidationError(
                "Le solde ne peut pas être négatif pour ce type de compte."
            )
        return value

    def create(self, validated_data):
        """
        Crée un compte et initialise le solde avec une transaction d'ajustement si nécessaire
        """
        from transactions.models import Transaction
        from datetime import date
        from decimal import Decimal

        initial_balance = validated_data.pop('balance', Decimal('0.00'))

        # Créer le compte avec balance à 0
        instance = super().create(validated_data)

        # Si un solde initial non nul est fourni, créer une transaction d'ajustement
        if initial_balance != 0:
            adjustment_sign = '+' if initial_balance > 0 else '-'

            Transaction.objects.create(
                user=instance.user,
                account=instance,
                type='adjustment',
                amount=abs(initial_balance),
                description=f"Solde initial du compte",
                date=date.today(),
                category=None,
                notes=f"ADJUSTMENT:{adjustment_sign}"
            )

        return instance

    def update(self, instance, validated_data):
        """
        Met à jour le compte et crée une transaction d'ajustement si le solde change
        """
        from transactions.models import Transaction
        from datetime import date
        from decimal import Decimal

        new_balance = validated_data.get('balance')

        # Si le solde change, créer une transaction d'ajustement
        if new_balance is not None:
            current_balance = instance.get_current_balance()
            difference = Decimal(str(new_balance)) - current_balance

            if difference != 0:
                # Créer une transaction d'ajustement
                # Stocker le signe dans les notes pour savoir comment appliquer l'ajustement
                adjustment_sign = '+' if difference > 0 else '-'

                Transaction.objects.create(
                    user=instance.user,
                    account=instance,
                    type='adjustment',
                    amount=abs(difference),
                    description=f"Ajustement de solde: {current_balance:.2f} → {new_balance:.2f}",
                    date=date.today(),
                    category=None,
                    notes=f"ADJUSTMENT:{adjustment_sign}"  # Stocker le signe
                )

            # Retirer balance des validated_data car on ne met pas à jour le champ directement
            validated_data.pop('balance', None)

        # Mettre à jour les autres champs
        return super().update(instance, validated_data)


class AccountListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des comptes
    """
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    current_balance = serializers.SerializerMethodField()
    projected_balance = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = [
            'id',
            'name',
            'account_type',
            'account_type_display',
            'balance',
            'current_balance',
            'projected_balance',
            'currency',
            'is_active',
        ]

    def get_current_balance(self, obj):
        """Solde actuel (excluant les transactions futures)"""
        return float(obj.get_current_balance())

    def get_projected_balance(self, obj):
        """Solde projeté (incluant les transactions futures)"""
        return float(obj.get_projected_balance())
