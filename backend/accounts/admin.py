from django.contrib import admin
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'account_type', 'balance', 'currency', 'is_active', 'created_at']
    list_filter = ['account_type', 'currency', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 50

    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'name', 'account_type', 'description')
        }),
        ('Finances', {
            'fields': ('balance', 'currency')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """
        Les superusers voient tous les comptes
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
