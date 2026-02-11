"""
WebAuthn utility functions for challenge management and credential handling.
"""
import base64
from typing import Optional, Union, List
from django.core.cache import cache
from django.conf import settings
from webauthn.helpers.structs import PublicKeyCredentialDescriptor
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url
from .models import WebAuthnCredential, User


def store_challenge(identifier: str, challenge: bytes, timeout: int = None) -> None:
    """
    Store a WebAuthn challenge in cache with expiration.

    Args:
        identifier: Unique identifier for the challenge (e.g., 'reg_123' or 'auth_session_key')
        challenge: The challenge bytes to store
        timeout: Cache timeout in seconds (defaults to WEBAUTHN_CHALLENGE_TIMEOUT)
    """
    if timeout is None:
        timeout = getattr(settings, 'WEBAUTHN_CHALLENGE_TIMEOUT', 60)

    cache_key = f'webauthn_challenge_{identifier}'
    # Store as base64 for cache compatibility
    challenge_b64 = bytes_to_base64url(challenge)
    cache.set(cache_key, challenge_b64, timeout)


def get_and_delete_challenge(identifier: str) -> Optional[bytes]:
    """
    Retrieve and immediately delete a challenge from cache.
    This ensures challenges are single-use.

    Args:
        identifier: Unique identifier for the challenge

    Returns:
        The challenge bytes if found, None otherwise
    """
    cache_key = f'webauthn_challenge_{identifier}'
    challenge_b64 = cache.get(cache_key)

    if challenge_b64 is None:
        return None

    # Delete immediately to prevent reuse
    cache.delete(cache_key)

    # Convert back to bytes
    try:
        return base64url_to_bytes(challenge_b64)
    except Exception:
        return None


def generate_challenge_key(user_or_session: Union[User, str], flow_type: str = 'reg') -> str:
    """
    Generate a cache key for storing challenges.

    Args:
        user_or_session: Either a User instance (for registration) or session key (for login)
        flow_type: 'reg' for registration, 'auth' for authentication

    Returns:
        A unique identifier for the challenge
    """
    if isinstance(user_or_session, User):
        return f'{flow_type}_{user_or_session.id}'
    else:
        return f'{flow_type}_{user_or_session}'


def get_user_credentials(user: User) -> List[PublicKeyCredentialDescriptor]:
    """
    Get all WebAuthn credentials for a user formatted as PublicKeyCredentialDescriptor.
    This is used for the exclude list during registration and allow list during authentication.

    Args:
        user: The User instance

    Returns:
        List of PublicKeyCredentialDescriptor objects
    """
    credentials = WebAuthnCredential.objects.filter(user=user)

    descriptors = []
    for cred in credentials:
        try:
            # Decode the base64-encoded credential_id
            cred_id_bytes = base64url_to_bytes(cred.credential_id)

            descriptor = PublicKeyCredentialDescriptor(
                id=cred_id_bytes,
                type="public-key"
            )
            descriptors.append(descriptor)
        except Exception as e:
            # Log and skip malformed credentials
            print(f"Warning: Skipping malformed credential {cred.id}: {e}")
            continue

    return descriptors


def increment_counter(credential: WebAuthnCredential, new_counter: int) -> bool:
    """
    Update the sign counter for a credential with validation.

    Args:
        credential: The WebAuthnCredential instance
        new_counter: The new counter value from authentication response

    Returns:
        True if counter was updated successfully, False if counter validation failed
    """
    if new_counter <= credential.counter:
        # Counter should always increment - possible replay attack
        return False

    credential.counter = new_counter
    return True


def encode_credential_data(credential_id: bytes, public_key: bytes) -> tuple:
    """
    Encode credential_id and public_key to base64url for database storage.

    Args:
        credential_id: The raw credential ID bytes
        public_key: The raw public key bytes

    Returns:
        Tuple of (credential_id_b64, public_key_b64)
    """
    credential_id_b64 = bytes_to_base64url(credential_id)
    public_key_b64 = bytes_to_base64url(public_key)
    return credential_id_b64, public_key_b64


def decode_credential_data(credential_id_b64: str, public_key_b64: str) -> tuple:
    """
    Decode base64url-encoded credential data back to bytes.

    Args:
        credential_id_b64: Base64url-encoded credential ID
        public_key_b64: Base64url-encoded public key

    Returns:
        Tuple of (credential_id_bytes, public_key_bytes)
    """
    credential_id_bytes = base64url_to_bytes(credential_id_b64)
    public_key_bytes = base64url_to_bytes(public_key_b64)
    return credential_id_bytes, public_key_bytes
