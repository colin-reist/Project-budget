"""
API Token authentication for external integrations like iOS Shortcuts.
"""
import secrets
from django.conf import settings
from django.db import models
from django.utils import timezone


class APIToken(models.Model):
    """
    API Token for persistent authentication (iOS Shortcuts, mobile apps, etc.)
    More secure than storing username/password in shortcuts.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_tokens',
        verbose_name='User'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Token Name',
        help_text='Friendly name for this token (e.g., "iPhone Shortcut")'
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name='Token',
        help_text='The actual API token (auto-generated)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Last Used'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active',
        help_text='Disable token without deleting it'
    )

    class Meta:
        db_table = 'api_token'
        verbose_name = 'API Token'
        verbose_name_plural = 'API Tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return secrets.token_urlsafe(48)  # 48 bytes = 64 characters

    def save(self, *args, **kwargs):
        """Auto-generate token if not provided"""
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)

    def update_last_used(self):
        """Update the last_used timestamp"""
        self.last_used = timezone.now()
        self.save(update_fields=['last_used'])


class PendingAlert(models.Model):
    """
    Alerte en attente pour l'utilisateur (ex: transaction iOS sans catégorie).
    """
    ALERT_TYPE_CHOICES = [
        ('unknown_category', 'Catégorie inconnue'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pending_alerts',
        verbose_name='Utilisateur'
    )
    type = models.CharField(
        max_length=30,
        choices=ALERT_TYPE_CHOICES,
        verbose_name="Type d'alerte"
    )
    payload = models.JSONField(
        default=dict,
        verbose_name='Données'
    )
    seen = models.BooleanField(
        default=False,
        verbose_name='Vue'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )

    class Meta:
        db_table = 'pending_alert'
        verbose_name = 'Alerte en attente'
        verbose_name_plural = 'Alertes en attente'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'seen']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.type} - {'vue' if self.seen else 'non vue'}"
