import calendar

from django.db import models
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


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
        related_name='budgets',
        null=True,
        blank=True,
        help_text='Catégorie associée (non requis pour les objectifs d\'épargne)'
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
    is_savings_goal = models.BooleanField(
        default=False,
        verbose_name='Objectif d\'épargne',
        help_text='Si coché, ce budget suit les transferts vers comptes épargne au lieu des dépenses'
    )
    is_mandatory_savings = models.BooleanField(
        default=False,
        verbose_name='Épargne obligatoire',
        help_text='Si coché, ce budget compte comme une dépense obligatoire mensuelle (ex: épargne de précaution, fond d\'urgence)'
    )
    savings_goal = models.ForeignKey(
        'budgets.SavingsGoal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budgets',
        verbose_name='Objectif d\'épargne lié'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.amount} ({self.get_period_display()})"

    def get_spent_amount(self):
        """
        Calcule le montant dépensé pour ce budget sur la période en cours
        (exclut les transactions avec une date future)
        Pour les objectifs d'épargne, calcule les transferts vers comptes épargne
        """
        from transactions.models import Transaction
        from accounts.models import Account
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

        # Calculer le total des dépenses (excluant les transactions futures)
        # Ne compter que les transactions avec une date <= aujourd'hui
        end = min(end, today)

        # Si c'est un objectif d'épargne, calculer les transferts vers comptes épargne
        if self.is_savings_goal:
            logger.debug(f"📊 Calcul objectif d'épargne: {self.name}")
            logger.debug(f"   Période: {start} à {end}")

            # Récupérer tous les comptes épargne de l'utilisateur
            savings_accounts = Account.objects.filter(
                user=self.user,
                account_type='savings',
                is_active=True
            )

            logger.debug(f"   Comptes épargne trouvés: {savings_accounts.count()}")
            for acc in savings_accounts:
                logger.debug(f"     - {acc.name} (ID: {acc.id}, type: {acc.account_type})")

            # Calculer le total des transferts vers ces comptes
            transfers = Transaction.objects.filter(
                user=self.user,
                type='transfer',
                destination_account__in=savings_accounts,
                date__gte=start,
                date__lte=end
            )

            logger.debug(f"   Transferts trouvés: {transfers.count()}")
            for trans in transfers:
                logger.debug(f"     - Date: {trans.date}, Montant: {trans.amount}, Vers: {trans.destination_account.name if trans.destination_account else 'N/A'}")

            total = transfers.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
            logger.debug(f"   💰 Total épargné: {total} CHF")
        else:
            # Budget normal: calculer les dépenses de la catégorie
            # Exclure les transactions de type 'adjustment' qui ne doivent pas compter dans les budgets
            logger.debug(f"📊 Calcul budget normal: {self.name}")
            logger.debug(f"   Catégorie: {self.category.name if self.category else 'N/A'}")
            logger.debug(f"   Période: {start} à {end}")

            expenses = Transaction.objects.filter(
                user=self.user,
                category=self.category,
                type='expense',
                date__gte=start,
                date__lte=end
            ).exclude(type='adjustment')

            logger.debug(f"   Dépenses trouvées: {expenses.count()}")
            total = expenses.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
            logger.debug(f"   💸 Total dépensé: {total} CHF")

        return total

    def get_spent_amount_for_period(self, year, month):
        """
        Calcule le montant dépensé pour ce budget sur un mois précis.
        Pour les mois passés, retourne le total complet du mois.
        Pour le mois en cours ou futur, cap à aujourd'hui.
        """
        from transactions.models import Transaction
        from accounts.models import Account
        from datetime import date

        today = date.today()

        start = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end = date(year, month, last_day)

        # Filtrer par les dates du budget si définies
        if self.start_date and start < self.start_date:
            start = self.start_date
        if self.end_date and end > self.end_date:
            end = self.end_date

        # Cap à aujourd'hui pour le mois courant ou futur
        cap = min(end, today) if (year, month) >= (today.year, today.month) else end

        if self.is_savings_goal:
            savings_accounts = Account.objects.filter(
                user=self.user,
                account_type='savings',
                is_active=True
            )
            total = Transaction.objects.filter(
                user=self.user,
                type='transfer',
                destination_account__in=savings_accounts,
                date__gte=start,
                date__lte=cap
            ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        else:
            total = Transaction.objects.filter(
                user=self.user,
                category=self.category,
                type='expense',
                date__gte=start,
                date__lte=cap
            ).exclude(type='adjustment').aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        return total

    def get_projected_amount(self):
        """
        Calcule le montant projeté (dépensé + transactions futures) pour ce budget sur la période en cours
        Inclut toutes les transactions jusqu'à la fin de la période, y compris les futures
        """
        from transactions.models import Transaction
        from accounts.models import Account
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

        # Calculer le total incluant les transactions futures (jusqu'à la fin de la période)
        if self.is_savings_goal:
            # Récupérer tous les comptes épargne de l'utilisateur
            savings_accounts = Account.objects.filter(
                user=self.user,
                account_type='savings',
                is_active=True
            )

            # Calculer le total des transferts vers ces comptes (incluant futures)
            transfers = Transaction.objects.filter(
                user=self.user,
                type='transfer',
                destination_account__in=savings_accounts,
                date__gte=start,
                date__lte=end
            )

            total = transfers.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        else:
            # Budget normal: calculer les dépenses de la catégorie (incluant futures)
            # Exclure les transactions de type 'adjustment' qui ne doivent pas compter dans les budgets
            expenses = Transaction.objects.filter(
                user=self.user,
                category=self.category,
                type='expense',
                date__gte=start,
                date__lte=end
            ).exclude(type='adjustment')

            total = expenses.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        return total

    def get_remaining_amount(self):
        """
        Calcule le montant restant du budget
        """
        return self.amount - self.get_spent_amount()

    def get_projected_remaining_amount(self):
        """
        Calcule le montant restant du budget en incluant les transactions futures
        """
        return self.amount - self.get_projected_amount()

    def get_percentage_used(self):
        """
        Calcule le pourcentage du budget utilisé
        """
        if self.amount == 0:
            return 0
        return float((self.get_spent_amount() / self.amount) * 100)

    def get_projected_percentage_used(self):
        """
        Calcule le pourcentage du budget utilisé en incluant les transactions futures
        """
        if self.amount == 0:
            return 0
        return float((self.get_projected_amount() / self.amount) * 100)

    def is_over_budget(self):
        """
        Vérifie si le budget est dépassé
        """
        return self.get_spent_amount() > self.amount

    def is_projected_over_budget(self):
        """
        Vérifie si le budget sera dépassé avec les transactions futures
        """
        return self.get_projected_amount() > self.amount

    def is_alert_triggered(self):
        """
        Vérifie si l'alerte doit être déclenchée
        """
        return self.get_percentage_used() >= self.alert_threshold

    def is_projected_alert_triggered(self):
        """
        Vérifie si l'alerte doit être déclenchée en incluant les transactions futures
        """
        return self.get_projected_percentage_used() >= self.alert_threshold


class SavingsGoal(models.Model):
    """
    Objectif d'épargne pour planifier l'achat d'un objet.
    """
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('reached', 'Atteint'),
        ('cancelled', 'Annulé'),
    ]

    FREQUENCY_CHOICES = [
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('yearly', 'Annuel'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='savings_goals'
    )
    label = models.CharField(
        max_length=200,
        verbose_name="Nom de l'objectif"
    )
    target_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Montant cible'
    )
    product_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='URL du produit'
    )
    product_image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="URL de l'image"
    )
    target_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Date cible'
    )
    saving_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Montant d'épargne par période"
    )
    saving_frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='monthly',
        verbose_name="Fréquence d'épargne"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Statut'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'savings_goal'
        verbose_name = "Objectif d'épargne"
        verbose_name_plural = "Objectifs d'épargne"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.label} - {self.target_amount} CHF"
