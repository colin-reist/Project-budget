from django.db import models
from django.db.models import Sum, Case, When, F, Value, DecimalField
from django.conf import settings
from decimal import Decimal


class Account(models.Model):
    """
    Représente un compte bancaire (compte courant, épargne, carte de crédit, etc.)
    """
    ACCOUNT_TYPES = [
        ('checking', 'Compte Courant'),
        ('savings', 'Compte Épargne'),
        ('credit_card', 'Carte de Crédit'),
        ('cash', 'Espèces'),
        ('investment', 'Investissement'),
        ('loan', 'Prêt'),
        ('other', 'Autre'),
    ]

    CURRENCY_CHOICES = [
        ('CHF', 'Franc Suisse'),
        ('EUR', 'Euro'),
        ('USD', 'Dollar US'),
        ('GBP', 'Livre Sterling'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='accounts',
        verbose_name='Utilisateur'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nom du compte'
    )
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPES,
        default='checking',
        verbose_name='Type de compte'
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name='Solde',
        help_text='Champ legacy - utiliser get_current_balance() ou get_projected_balance() pour obtenir le solde'
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='CHF',
        verbose_name='Devise'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Compte actif'
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
        db_table = 'account'
        verbose_name = 'Compte'
        verbose_name_plural = 'Comptes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['account_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()}) - {self.balance} {self.currency}"

    def update_balance(self, amount):
        """
        Met à jour le solde du compte
        """
        self.balance += amount
        self.save(update_fields=['balance', 'updated_at'])

    def _aggregate_balance(self, date_filter=None):
        """Calcule le solde via SQL aggregation. date_filter est un Q() optionnel."""
        from transactions.models import Transaction

        qs = Transaction.objects.filter(account=self)
        if date_filter is not None:
            qs = qs.filter(date_filter)

        result = qs.exclude(type='adjustment').aggregate(
            total=Sum(Case(
                When(type='income', then=F('amount')),
                When(type='expense', then=-F('amount')),
                When(type='transfer', destination_account__isnull=False, then=-F('amount')),
                default=Value(Decimal('0')),
                output_field=DecimalField(max_digits=15, decimal_places=2),
            ))
        )

        # Adjustments : signe encodé dans notes, traitement Python sur sous-ensemble limité
        adj_qs = qs.filter(type='adjustment')
        adj_balance = Decimal('0.00')
        for t in adj_qs:
            if t.notes and 'ADJUSTMENT:' in t.notes:
                sign = t.notes.split('ADJUSTMENT:')[1].strip()
                adj_balance += t.amount if sign.startswith('+') else -t.amount

        incoming_qs = Transaction.objects.filter(destination_account=self, type='transfer')
        if date_filter is not None:
            incoming_qs = incoming_qs.filter(date_filter)
        incoming = incoming_qs.aggregate(total=Sum('amount'))['total'] or Decimal('0')

        return (result['total'] or Decimal('0')) + adj_balance + incoming

    def get_current_balance(self):
        """Retourne le solde actuel en excluant les transactions futures."""
        from datetime import date
        from django.db.models import Q
        return self._aggregate_balance(Q(date__lte=date.today()))

    def get_projected_balance(self):
        """Retourne le solde projeté incluant toutes les transactions (même futures)."""
        return self._aggregate_balance()
