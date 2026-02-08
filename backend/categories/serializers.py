from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Category
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'user',
            'name',
            'type',
            'type_display',
            'icon',
            'color',
            'parent_category',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'type_display']


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des catégories
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'type_display', 'icon', 'color', 'is_active']
