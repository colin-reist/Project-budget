"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from authentication.ios_views import (
    ios_create_transaction,
    alert_list,
    alert_count,
    alert_dismiss,
)
from budgets.views import SavingsGoalViewSet

savings_router = SimpleRouter()
savings_router.register(r'savings-goals', SavingsGoalViewSet, basename='savings-goal')

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/categories/', include('categories.urls')),
    path('api/v1/transactions/', include('transactions.urls')),
    path('api/v1/budgets/', include('budgets.urls')),
    path('api/v1/', include(savings_router.urls)),

    # iOS integration
    path('api/v1/ios/transaction/', ios_create_transaction, name='ios-transaction'),

    # Alertes
    path('api/v1/alerts/', alert_list, name='alert-list'),
    path('api/v1/alerts/count/', alert_count, name='alert-count'),
    path('api/v1/alerts/<int:alert_id>/dismiss/', alert_dismiss, name='alert-dismiss'),
]
