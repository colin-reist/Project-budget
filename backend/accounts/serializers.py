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
        if value < 0 and self.instance and self.instance.account_type not in ['credit_card', 'loan']:
            raise serializers.ValidationError(
                "Le solde ne peut pas être négatif pour ce type de compte."
            )
        return value


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
