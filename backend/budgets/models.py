from django.db import models
from django.conf import settings
from decimal import Decimal


class Budget(models.Model):
    """
    Modèle pour définir des budgets par catégorie
    """
    PERIOD_CHOICES = [
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('yearly', 'Annuel'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='monthly')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    alert_threshold = models.IntegerField(
        default=80,
        help_text="Pourcentage du budget à partir duquel une alerte est déclenchée"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'category', 'period', 'start_date']

    def __str__(self):
        return f"{self.name} - {self.amount} ({self.get_period_display()})"

    def get_spent_amount(self):
        """
        Calcule le montant dépensé pour ce budget sur la période en cours
        """
        from transactions.models import Transaction
        from datetime import date, timedelta

        today = date.today()

        # Calculer la période en cours
        if self.period == 'weekly':
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
        elif self.period == 'monthly':
            start = date(today.year, today.month, 1)
            if today.month == 12:
                end = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        else:  # yearly
            start = date(today.year, 1, 1)
            end = date(today.year, 12, 31)

        # Filtrer par les dates du budget si définies
        if self.start_date and start < self.start_date:
            start = self.start_date
        if self.end_date and end > self.end_date:
            end = self.end_date

        # Calculer le total des dépenses
        total = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            type='expense',
            date__gte=start,
            date__lte=end
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        return total

    def get_remaining_amount(self):
        """
        Calcule le montant restant du budget
        """
        return self.amount - self.get_spent_amount()

    def get_percentage_used(self):
        """
        Calcule le pourcentage du budget utilisé
        """
        if self.amount == 0:
            return 0
        return float((self.get_spent_amount() / self.amount) * 100)

    def is_over_budget(self):
        """
        Vérifie si le budget est dépassé
        """
        return self.get_spent_amount() > self.amount

    def is_alert_triggered(self):
        """
        Vérifie si l'alerte doit être déclenchée
        """
        return self.get_percentage_used() >= self.alert_threshold
