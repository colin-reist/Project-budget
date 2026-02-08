from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'type', 'amount', 'account', 'category', 'date', 'user', 'created_at']
    list_filter = ['type', 'date', 'is_recurring', 'created_at']
    search_fields = ['description', 'notes', 'user__username']
    list_per_page = 50
    date_hierarchy = 'date'
