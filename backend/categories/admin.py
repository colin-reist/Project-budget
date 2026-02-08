from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'icon', 'color', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'created_at']
    search_fields = ['name', 'user__username']
    list_per_page = 50
