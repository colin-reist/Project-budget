from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category
from .serializers import CategorySerializer, CategoryListSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les catégories
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_active', 'parent_category']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['type', 'name']

    def get_queryset(self):
        """
        Retourne uniquement les catégories de l'utilisateur connecté
        """
        return Category.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Utilise un serializer différent pour la liste
        """
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer

    def perform_create(self, serializer):
        """
        Associe automatiquement l'utilisateur connecté à la catégorie
        """
        serializer.save(user=self.request.user)
