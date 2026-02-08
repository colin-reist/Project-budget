from django.contrib import admin
from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category', 'amount', 'period', 'start_date', 'end_date', 'is_active', 'created_at']
    list_filter = ['period', 'is_active', 'created_at']
    search_fields = ['name', 'user__username', 'category__name']
    list_per_page = 50
    date_hierarchy = 'start_date'
