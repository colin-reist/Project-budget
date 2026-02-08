from django.db import models
from django.conf import settings


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
        verbose_name='Solde'
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
