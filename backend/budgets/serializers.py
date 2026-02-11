import math
from datetime import date

from rest_framework import serializers
from .models import Budget, SavingsGoal
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
    projected_amount = serializers.SerializerMethodField()
    projected_remaining_amount = serializers.SerializerMethodField()
    projected_percentage_used = serializers.SerializerMethodField()
    is_projected_over_budget = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_details', 'name', 'amount', 'period',
            'period_display', 'start_date', 'end_date', 'is_active', 'is_savings_goal',
            'spent_amount', 'remaining_amount', 'percentage_used', 'is_over_budget',
            'projected_amount', 'projected_remaining_amount', 'projected_percentage_used',
            'is_projected_over_budget', 'created_at'
        ]

    def get_spent_amount(self, obj):
        return float(obj.get_spent_amount())

    def get_remaining_amount(self, obj):
        return float(obj.get_remaining_amount())

    def get_percentage_used(self, obj):
        return round(obj.get_percentage_used(), 2)

    def get_is_over_budget(self, obj):
        return obj.is_over_budget()

    def get_projected_amount(self, obj):
        return float(obj.get_projected_amount())

    def get_projected_remaining_amount(self, obj):
        return float(obj.get_projected_remaining_amount())

    def get_projected_percentage_used(self, obj):
        return round(obj.get_projected_percentage_used(), 2)

    def get_is_projected_over_budget(self, obj):
        return obj.is_projected_over_budget()


class SavingsGoalSerializer(serializers.ModelSerializer):
    """
    Serializer pour les objectifs d'épargne avec calculs automatiques.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    calculated_result = serializers.SerializerMethodField()
    linked_budgets = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    saving_frequency_display = serializers.CharField(source='get_saving_frequency_display', read_only=True)

    class Meta:
        model = SavingsGoal
        fields = [
            'id', 'user', 'label', 'target_amount', 'product_url',
            'product_image_url', 'target_date', 'saving_amount',
            'saving_frequency', 'saving_frequency_display', 'status',
            'status_display', 'calculated_result', 'linked_budgets',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_calculated_result(self, obj):
        """Calcule la date cible (Mode A) ou le montant par période (Mode B)."""
        if obj.saving_amount and not obj.target_date:
            # Mode A : épargne connue → calculer la date
            if obj.saving_amount <= 0:
                return None
            periods_needed = math.ceil(float(obj.target_amount) / float(obj.saving_amount))
            today = date.today()

            if obj.saving_frequency == 'daily':
                from datetime import timedelta
                target = today + timedelta(days=periods_needed)
            elif obj.saving_frequency == 'weekly':
                from datetime import timedelta
                target = today + timedelta(weeks=periods_needed)
            elif obj.saving_frequency == 'monthly':
                month = today.month + periods_needed
                year = today.year + (month - 1) // 12
                month = (month - 1) % 12 + 1
                day = min(today.day, 28)
                target = date(year, month, day)
            else:  # yearly
                target = date(today.year + periods_needed, today.month, today.day)

            return {
                'mode': 'date_calculated',
                'target_date': str(target),
                'periods_needed': periods_needed,
            }

        elif obj.target_date:
            # Mode B : date connue → calculer le montant
            today = date.today()
            if obj.target_date <= today:
                return {'mode': 'amount_calculated', 'saving_amount': float(obj.target_amount), 'periods_needed': 1}

            if obj.saving_frequency == 'daily':
                periods = (obj.target_date - today).days
            elif obj.saving_frequency == 'weekly':
                periods = max(1, (obj.target_date - today).days // 7)
            elif obj.saving_frequency == 'monthly':
                periods = max(1, (obj.target_date.year - today.year) * 12 + (obj.target_date.month - today.month))
            else:  # yearly
                periods = max(1, obj.target_date.year - today.year)

            amount_per_period = float(obj.target_amount) / periods
            return {
                'mode': 'amount_calculated',
                'saving_amount': round(amount_per_period, 2),
                'periods_needed': periods,
            }

        return None

    def get_linked_budgets(self, obj):
        budgets = Budget.objects.filter(savings_goal=obj)
        return [{'id': b.id, 'name': b.name, 'amount': float(b.amount)} for b in budgets]


class SavingsGoalListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des objectifs d'épargne.
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SavingsGoal
        fields = [
            'id', 'label', 'target_amount', 'target_date', 'saving_amount',
            'saving_frequency', 'status', 'status_display', 'created_at'
        ]
