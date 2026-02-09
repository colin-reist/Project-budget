from rest_framework import serializers
from .models import Budget
from categories.serializers import CategoryListSerializer


class BudgetSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour Budget avec toutes les informations calculées
    """
    category_details = CategoryListSerializer(source='category', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    spent_amount = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    percentage_used = serializers.SerializerMethodField()
    is_over_budget = serializers.SerializerMethodField()
    is_alert_triggered = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'id', 'user', 'category', 'category_details', 'name', 'amount',
            'period', 'period_display', 'start_date', 'end_date', 'alert_threshold',
            'is_active', 'is_savings_goal', 'spent_amount', 'remaining_amount', 'percentage_used',
            'is_over_budget', 'is_alert_triggered', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_spent_amount(self, obj):
        return float(obj.get_spent_amount())

    def get_remaining_amount(self, obj):
        return float(obj.get_remaining_amount())

    def get_percentage_used(self, obj):
        return round(obj.get_percentage_used(), 2)

    def get_is_over_budget(self, obj):
        return obj.is_over_budget()

    def get_is_alert_triggered(self, obj):
        return obj.is_alert_triggered()

    def validate_category(self, value):
        """
        Vérifie que la catégorie appartient à l'utilisateur
        """
        # Si c'est None (objectif d'épargne), c'est OK
        if value is None:
            return value

        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError(
                "Vous ne pouvez créer un budget que pour vos propres catégories."
            )
        return value

    def validate(self, data):
        """
        Validations supplémentaires
        """
        # Pour les objectifs d'épargne, la catégorie n'est pas requise
        is_savings_goal = data.get('is_savings_goal', False)
        category = data.get('category')

        if not is_savings_goal and not category:
            raise serializers.ValidationError({
                'category': 'Une catégorie est requise pour les budgets normaux.'
            })

        if is_savings_goal and category:
            # Si c'est un objectif d'épargne, on ignore la catégorie
            data['category'] = None

        # Vérifier que end_date est après start_date
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError({
                    'end_date': 'La date de fin doit être après la date de début.'
                })

        # Vérifier que alert_threshold est entre 0 et 100
        if 'alert_threshold' in data:
            if data['alert_threshold'] < 0 or data['alert_threshold'] > 100:
                raise serializers.ValidationError({
                    'alert_threshold': 'Le seuil d\'alerte doit être entre 0 et 100.'
                })

        return data


class BudgetListSerializer(serializers.ModelSerializer):
    """
    Serializer optimisé pour la liste des budgets
    """
    category_details = CategoryListSerializer(source='category', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    spent_amount = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    percentage_used = serializers.SerializerMethodField()
    is_over_budget = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_details', 'name', 'amount', 'period',
            'period_display', 'start_date', 'end_date', 'is_active', 'is_savings_goal',
            'spent_amount', 'remaining_amount', 'percentage_used', 'is_over_budget', 'created_at'
        ]

    def get_spent_amount(self, obj):
        return float(obj.get_spent_amount())

    def get_remaining_amount(self, obj):
        return float(obj.get_remaining_amount())

    def get_percentage_used(self, obj):
        return round(obj.get_percentage_used(), 2)

    def get_is_over_budget(self, obj):
        return obj.is_over_budget()
