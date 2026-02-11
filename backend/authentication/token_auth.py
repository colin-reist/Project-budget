"""
Custom DRF authentication backend for API tokens (iOS Shortcuts, etc.).
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .api_token import APIToken


class APITokenAuthentication(BaseAuthentication):
    """
    Authentification par API token pour les intégrations externes.
    Header attendu : Authorization: Bearer <token>
    Ignore les JWT (qui contiennent des points).
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None

        token_value = auth_header[7:]

        # Les JWT contiennent des points, on les ignore
        if '.' in token_value:
            return None

        try:
            api_token = APIToken.objects.get(token=token_value, is_active=True)
            api_token.update_last_used()
            return (api_token.user, api_token)
        except APIToken.DoesNotExist:
            raise AuthenticationFailed('Token invalide ou désactivé.')
