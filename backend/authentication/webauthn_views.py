"""
WebAuthn/Passkey authentication views.
Implements registration, authentication, and credential management endpoints.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
import json

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    AttestationConveyancePreference,
    PublicKeyCredentialDescriptor,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

from .models import WebAuthnCredential
from .serializers import UserSerializer
from .webauthn_serializers import (
    WebAuthnRegisterBeginSerializer,
    WebAuthnRegisterCompleteSerializer,
    WebAuthnLoginCompleteSerializer,
    WebAuthnCredentialSerializer,
)
from .webauthn_utils import (
    store_challenge,
    get_and_delete_challenge,
    generate_challenge_key,
    get_user_credentials,
    increment_counter,
    encode_credential_data,
    decode_credential_data,
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webauthn_register_begin(request):
    """
    Begin WebAuthn registration flow.
    Generates registration options and stores challenge.

    POST /api/v1/auth/webauthn/register/begin/
    Body: { "username": "optional_username" }

    Returns registration options for browser to create credential.
    """
    serializer = WebAuthnRegisterBeginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user

    # Get existing credentials to exclude during registration
    existing_credentials = get_user_credentials(user)

    try:
        # Generate registration options
        options = generate_registration_options(
            rp_id=settings.WEBAUTHN_RP_ID,
            rp_name=settings.WEBAUTHN_RP_NAME,
            user_id=str(user.id).encode('utf-8'),
            user_name=user.username,
            user_display_name=user.get_full_name() or user.username,
            exclude_credentials=existing_credentials,
            attestation=AttestationConveyancePreference.NONE,
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
            ],
        )

        # Store challenge for verification
        challenge_key = generate_challenge_key(user, 'reg')
        store_challenge(challenge_key, options.challenge)

        # Convert options to JSON-serializable format
        options_json = options_to_json(options)
        options_dict = json.loads(options_json)

        return Response(options_dict, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"WebAuthn registration error: {error_detail}")
        return Response({
            'error': f'Failed to generate registration options: {str(e)}',
            'detail': error_detail if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webauthn_register_complete(request):
    """
    Complete WebAuthn registration flow.
    Verifies credential and saves to database.

    POST /api/v1/auth/webauthn/register/complete/
    Body: {
        "credential": { ... },
        "device_name": "optional_device_name"
    }

    Returns success message and credential ID.
    """
    serializer = WebAuthnRegisterCompleteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    credential_data = serializer.validated_data['credential']
    device_name = serializer.validated_data.get('device_name', '')

    # Retrieve and delete challenge
    challenge_key = generate_challenge_key(user, 'reg')
    expected_challenge = get_and_delete_challenge(challenge_key)

    if expected_challenge is None:
        return Response({
            'error': 'Challenge expired or not found. Please try again.'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Verify registration response
        verification = verify_registration_response(
            credential=credential_data,
            expected_challenge=expected_challenge,
            expected_origin=settings.WEBAUTHN_ORIGIN,
            expected_rp_id=settings.WEBAUTHN_RP_ID,
        )

        # Encode credential data for storage
        credential_id_b64, public_key_b64 = encode_credential_data(
            verification.credential_id,
            verification.credential_public_key
        )

        # Check if credential already exists
        if WebAuthnCredential.objects.filter(credential_id=credential_id_b64).exists():
            return Response({
                'error': 'This credential is already registered.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create new credential record
        credential = WebAuthnCredential.objects.create(
            user=user,
            credential_id=credential_id_b64,
            public_key=public_key_b64,
            counter=verification.sign_count,
            device_name=device_name or 'Passkey',
        )

        return Response({
            'message': 'Passkey registered successfully.',
            'credential_id': credential.id,
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': f'Registration verification failed: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def webauthn_login_begin(request):
    """
    Begin WebAuthn authentication flow.
    Generates authentication options and stores challenge.

    POST /api/v1/auth/webauthn/login/begin/

    Returns authentication options for browser.
    """
    try:
        # Generate authentication options
        # We use empty allow_credentials for usernameless flow
        options = generate_authentication_options(
            rp_id=settings.WEBAUTHN_RP_ID,
            user_verification=UserVerificationRequirement.REQUIRED,
        )

        # Store challenge with session key
        # Since user is not authenticated yet, use session key
        if not request.session.session_key:
            request.session.create()
        challenge_key = generate_challenge_key(request.session.session_key, 'auth')
        store_challenge(challenge_key, options.challenge)

        # Convert options to JSON
        options_json = options_to_json(options)
        options_dict = json.loads(options_json)

        return Response(options_dict, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"WebAuthn authentication options error: {error_detail}")
        return Response({
            'error': f'Failed to generate authentication options: {str(e)}',
            'detail': error_detail if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def webauthn_login_complete(request):
    """
    Complete WebAuthn authentication flow.
    Verifies credential and returns JWT tokens.

    POST /api/v1/auth/webauthn/login/complete/
    Body: { "credential": { ... } }

    Returns JWT tokens and user data.
    """
    serializer = WebAuthnLoginCompleteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    credential_data = serializer.validated_data['credential']

    # Extract credential ID from response
    try:
        credential_id = credential_data.get('id') or credential_data.get('rawId')
        if not credential_id:
            return Response({
                'error': 'Credential ID not found in response.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find credential in database
        try:
            credential = WebAuthnCredential.objects.get(credential_id=credential_id)
        except WebAuthnCredential.DoesNotExist:
            return Response({
                'error': 'Credential not found. Please register first.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        user = credential.user

        # Retrieve and delete challenge
        challenge_key = generate_challenge_key(request.session.session_key, 'auth')
        expected_challenge = get_and_delete_challenge(challenge_key)

        if expected_challenge is None:
            return Response({
                'error': 'Challenge expired or not found. Please try again.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Decode stored public key
        _, public_key_bytes = decode_credential_data(
            credential.credential_id,
            credential.public_key
        )

        # Verify authentication response
        verification = verify_authentication_response(
            credential=credential_data,
            expected_challenge=expected_challenge,
            expected_origin=settings.WEBAUTHN_ORIGIN,
            expected_rp_id=settings.WEBAUTHN_RP_ID,
            credential_public_key=public_key_bytes,
            credential_current_sign_count=credential.counter,
        )

        # Validate counter incremented (replay prevention)
        if not increment_counter(credential, verification.new_sign_count):
            return Response({
                'error': 'Invalid credential counter. Possible replay attack detected.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update credential
        credential.last_used = timezone.now()
        credential.save()

        # Generate JWT tokens (same as password login)
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': f'Authentication verification failed: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def webauthn_credentials_list(request):
    """
    List all WebAuthn credentials for the authenticated user.

    GET /api/v1/auth/webauthn/credentials/

    Returns list of user's credentials.
    """
    credentials = WebAuthnCredential.objects.filter(user=request.user).order_by('-created_at')
    serializer = WebAuthnCredentialSerializer(credentials, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def webauthn_credential_delete(request, credential_id):
    """
    Delete a specific WebAuthn credential.

    DELETE /api/v1/auth/webauthn/credentials/{credential_id}/

    Returns success message.
    """
    try:
        credential = WebAuthnCredential.objects.get(
            id=credential_id,
            user=request.user
        )
        credential.delete()

        return Response({
            'message': 'Passkey deleted successfully.'
        }, status=status.HTTP_200_OK)

    except WebAuthnCredential.DoesNotExist:
        return Response({
            'error': 'Credential not found or does not belong to you.'
        }, status=status.HTTP_404_NOT_FOUND)
