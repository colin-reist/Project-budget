from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    login_view,
    user_profile_view,
    logout_view,
    UserProfileViewSet
)
from .webauthn_views import (
    webauthn_register_begin,
    webauthn_register_complete,
    webauthn_login_begin,
    webauthn_login_complete,
    webauthn_credentials_list,
    webauthn_credential_delete,
)
from .ios_views import token_list, token_create, token_delete

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
    path('profile/change_password/', UserProfileViewSet.as_view({'post': 'change_password'}), name='profile-change-password'),
    path('profile/delete_account/', UserProfileViewSet.as_view({'delete': 'delete_account'}), name='profile-delete-account'),
    path('profile/setup_recurring_salary/', UserProfileViewSet.as_view({'post': 'setup_recurring_salary'}), name='profile-setup-recurring-salary'),

    # WebAuthn / Passkey authentication
    path('webauthn/register/begin/', webauthn_register_begin, name='webauthn-register-begin'),
    path('webauthn/register/complete/', webauthn_register_complete, name='webauthn-register-complete'),
    path('webauthn/login/begin/', webauthn_login_begin, name='webauthn-login-begin'),
    path('webauthn/login/complete/', webauthn_login_complete, name='webauthn-login-complete'),
    path('webauthn/credentials/', webauthn_credentials_list, name='webauthn-credentials-list'),
    path('webauthn/credentials/<int:credential_id>/', webauthn_credential_delete, name='webauthn-credential-delete'),

    # API Tokens
    path('tokens/', token_list, name='token-list'),
    path('tokens/create/', token_create, name='token-create'),
    path('tokens/<int:token_id>/', token_delete, name='token-delete'),
]
