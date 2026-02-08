from django.db import models
from django.conf import settings
from decimal import Decimal


class Transaction(models.Model):
    """
    Transaction financière (revenu, dépense, ou transfert)
    """
    TYPE_CHOICES = [
        ('income', 'Revenu'),
        ('expense', 'Dépense'),
        ('transfer', 'Transfert'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Utilisateur'
    )
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Compte'
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name='Catégorie'
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name='Type'
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Montant'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='Description'
    )
    date = models.DateField(
        verbose_name='Date'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notes'
    )
    # Pour les transferts
    destination_account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incoming_transfers',
        verbose_name='Compte destination'
    )
    # Récurrence
    is_recurring = models.BooleanField(
        default=False,
        verbose_name='Récurrent'
    )
    recurrence_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Quotidien'),
            ('weekly', 'Hebdomadaire'),
            ('monthly', 'Mensuel'),
            ('yearly', 'Annuel'),
        ],
        null=True,
        blank=True,
        verbose_name='Fréquence'
    )
    recurrence_interval = models.IntegerField(
        default=1,
        null=True,
        blank=True,
        verbose_name='Intervalle'
    )
    recurrence_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fin de récurrence'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Date de modification'
    )

    class Meta:
        db_table = 'transaction'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['account', 'date']),
            models.Index(fields=['category', 'date']),
            models.Index(fields=['type', 'date']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.amount} - {self.date}"

    def save(self, *args, **kwargs):
        """
        Sauvegarde la transaction sans mettre à jour le solde du compte
        (le solde est calculé dynamiquement à partir des transactions)
        """
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Supprime la transaction (le solde est recalculé dynamiquement)
        """
        super().delete(*args, **kwargs)
