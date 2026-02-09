from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    login_view,
    user_profile_view,
    logout_view,
    UserProfileViewSet
)

app_name = 'authentication'

urlpatterns = [
    # User registration
    path('register/', RegisterView.as_view(), name='register'),

    # User login (traditional username/password)
    path('login/', login_view, name='login'),

    # Get current user profile
    path('me/', user_profile_view, name='user-profile'),

    # Logout
    path('logout/', logout_view, name='logout'),

    # JWT token refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # User financial profile
    path('profile/me/', UserProfileViewSet.as_view({'get': 'me'}), name='profile-me'),
    path('profile/update/', UserProfileViewSet.as_view({'put': 'update_me', 'patch': 'update_me'}), name='profile-update'),
]
