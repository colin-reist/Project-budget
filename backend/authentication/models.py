from django.contrib.auth.models import AbstractUser
from django.db import models
from .api_token import APIToken, PendingAlert  # noqa: F401


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    Inherits standard fields:
    - username
    - email
    - first_name
    - last_name
    - password
    - is_staff
    - is_active
    - is_superuser
    - date_joined
    - last_login

    Additional fields can be added here for future features.
    """
    email = models.EmailField(unique=True, verbose_name="Email address")

    # Make email required
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username


class WebAuthnCredential(models.Model):
    """
    WebAuthn credential for passwordless authentication using passkeys.
    Stores public key and metadata for each registered authenticator.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='webauthn_credentials',
        verbose_name="User"
    )
    credential_id = models.TextField(
        unique=True,
        verbose_name="Credential ID",
        help_text="Unique identifier for this WebAuthn credential"
    )
    public_key = models.TextField(
        verbose_name="Public Key",
        help_text="Base64-encoded public key"
    )
    counter = models.IntegerField(
        default=0,
        verbose_name="Sign Counter",
        help_text="Counter to prevent replay attacks"
    )
    device_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Device Name",
        help_text="Friendly name for this device (e.g., 'Proton Pass')"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Used"
    )

    class Meta:
        db_table = 'webauthn_credential'
        verbose_name = 'WebAuthn Credential'
        verbose_name_plural = 'WebAuthn Credentials'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['credential_id']),
        ]

    def __str__(self):
        device = self.device_name or "Unknown Device"
        return f"{self.user.username} - {device}"


class UserProfile(models.Model):
    """
    Profil utilisateur contenant les informations financières
    """
    CURRENCY_CHOICES = [
        ('CHF', 'Franc Suisse'),
        ('EUR', 'Euro'),
        ('USD', 'Dollar US'),
        ('GBP', 'Livre Sterling'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Utilisateur'
    )
    monthly_income = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name='Revenu mensuel',
        help_text='Revenu mensuel total disponible pour les budgets'
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='CHF',
        verbose_name='Devise'
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
        db_table = 'user_profile'
        verbose_name = 'Profil Utilisateur'
        verbose_name_plural = 'Profils Utilisateurs'

    def __str__(self):
        return f"Profil de {self.user.username} - Revenu: {self.monthly_income} {self.currency}/mois"

    def get_available_budget(self):
        """
        Calcule le budget disponible (revenu - budgets alloués)
        Les objectifs d'épargne ne sont PAS comptés dans les budgets alloués
        """
        from budgets.models import Budget
        from decimal import Decimal

        # Récupérer tous les budgets actifs mensuels (SAUF les objectifs d'épargne)
        monthly_budgets = Budget.objects.filter(
            user=self.user,
            is_active=True,
            period='monthly',
            is_savings_goal=False
        )

        # Calculer le total des budgets mensuels
        total_allocated = monthly_budgets.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        # Calculer le total des objectifs d'épargne mensuels
        savings_goals = Budget.objects.filter(
            user=self.user,
            is_active=True,
            period='monthly',
            is_savings_goal=True
        )
        total_savings_goal = savings_goals.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

        # Budget disponible = revenu - budgets alloués (sans l'épargne)
        available = self.monthly_income - total_allocated

        return {
            'monthly_income': float(self.monthly_income),
            'total_allocated': float(total_allocated),
            'total_savings_goal': float(total_savings_goal),
            'available': float(available),
            'percentage_allocated': float((total_allocated / self.monthly_income * 100)) if self.monthly_income > 0 else 0
        }
