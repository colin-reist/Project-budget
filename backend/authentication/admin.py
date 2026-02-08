from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, WebAuthnCredential


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model.
    Extends Django's built-in UserAdmin with custom fields.
    """
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']


@admin.register(WebAuthnCredential)
class WebAuthnCredentialAdmin(admin.ModelAdmin):
    """
    Admin interface for WebAuthn credentials.
    """
    list_display = ['user', 'device_name', 'counter', 'created_at', 'last_used']
    list_filter = ['created_at', 'last_used']
    search_fields = ['user__username', 'user__email', 'device_name', 'credential_id']
    readonly_fields = ['credential_id', 'public_key', 'counter', 'created_at', 'last_used']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        """
        Disable adding credentials through admin.
        They should only be created through WebAuthn registration flow.
        """
        return False
