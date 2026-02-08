from django.contrib.auth.models import AbstractUser
from django.db import models


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
