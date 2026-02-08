from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import AccountViewSet

router = SimpleRouter()
router.register(r'', AccountViewSet, basename='account')

urlpatterns = [
    path('', include(router.urls)),
]
