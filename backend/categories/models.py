from django.db import models
from django.conf import settings


class Category(models.Model):
    """
    Catégorie pour les transactions (revenus/dépenses)
    """
    TYPE_CHOICES = [
        ('income', 'Revenu'),
        ('expense', 'Dépense'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='Utilisateur'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Nom'
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name='Type'
    )
    icon = models.CharField(
        max_length=50,
        default='i-heroicons-tag',
        verbose_name='Icône'
    )
    color = models.CharField(
        max_length=20,
        default='blue',
        verbose_name='Couleur'
    )
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name='Catégorie parente'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )

    class Meta:
        db_table = 'category'
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['type', 'name']
        unique_together = [['user', 'name', 'type']]
        indexes = [
            models.Index(fields=['user', 'type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
