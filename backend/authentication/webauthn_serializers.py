"""
Serializers for WebAuthn authentication endpoints.
"""
from rest_framework import serializers
from .models import WebAuthnCredential


class WebAuthnRegisterBeginSerializer(serializers.Serializer):
    """
    Serializer for initiating WebAuthn registration.
    """
    username = serializers.CharField(required=False, help_text="Username for logging (optional during registration)")

    def validate_username(self, value):
        """
        Validate username if provided.
        """
        if value and len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        return value


class WebAuthnRegisterCompleteSerializer(serializers.Serializer):
    """
    Serializer for completing WebAuthn registration.
    Receives the credential from the browser and validates it.
    """
    credential = serializers.JSONField(required=True, help_text="WebAuthn credential response from browser")
    device_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
        help_text="Friendly name for this device (e.g., 'iPhone 13', 'YubiKey')"
    )

    def validate_credential(self, value):
        """
        Validate that credential contains required fields.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Credential must be a JSON object.")

        required_fields = ['id', 'rawId', 'response', 'type']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Credential missing required field: {field}")

        return value


class WebAuthnLoginCompleteSerializer(serializers.Serializer):
    """
    Serializer for completing WebAuthn authentication.
    Receives the credential assertion from the browser.
    """
    credential = serializers.JSONField(required=True, help_text="WebAuthn credential assertion from browser")

    def validate_credential(self, value):
        """
        Validate that credential contains required fields.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Credential must be a JSON object.")

        required_fields = ['id', 'rawId', 'response', 'type']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Credential missing required field: {field}")

        return value


class WebAuthnCredentialSerializer(serializers.ModelSerializer):
    """
    Serializer for WebAuthn credentials.
    Used for listing user's registered credentials.
    """
    class Meta:
        model = WebAuthnCredential
        fields = [
            'id',
            'credential_id',
            'device_name',
            'counter',
            'created_at',
            'last_used',
        ]
        read_only_fields = [
            'id',
            'credential_id',
            'counter',
            'created_at',
            'last_used',
        ]
