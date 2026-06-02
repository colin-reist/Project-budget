from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Used for displaying user information.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles password validation and user creation.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': True}
        }

    def validate(self, attrs):
        """
        Validate that passwords match.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def validate_email(self, value):
        """
        Check that email is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """
        Check that username is unique.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        """
        Create and return a new user with encrypted password.
        """
        # Remove password2 as it's not needed for user creation
        validated_data.pop('password2')

        # Create user with create_user to properly hash password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Accepts username/email and password.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user information.
    """
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom user data to the response
        data['user'] = UserSerializer(self.user).data

        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.

    Exposes both UserProfile fields and selected User model fields (via source='user.*').
    first_name and last_name are writable and saved back to the User model via override update().
    username, email, date_joined, last_login are read-only projections from the User model.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    available_budget_info = serializers.SerializerMethodField()

    # Read-only fields sourced from the related User model
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    last_login = serializers.DateTimeField(source='user.last_login', read_only=True)

    # Writable fields that persist to the User model
    first_name = serializers.CharField(
        source='user.first_name', required=False, allow_blank=True, default=''
    )
    last_name = serializers.CharField(
        source='user.last_name', required=False, allow_blank=True, default=''
    )

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            # User model projections
            'username',
            'email',
            'first_name',
            'last_name',
            'date_joined',
            'last_login',
            # Financial
            'monthly_income',
            'currency',
            'salary_day',
            # Personal info
            'phone',
            'birth_date',
            # Locale
            'language',
            'timezone_pref',
            'city',
            'country',
            # Budget preferences
            'budget_start_day',
            'budget_rollover',
            'budget_roundup',
            'budget_roundup_amount',
            'show_cents',
            # Computed
            'available_budget_info',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'available_budget_info',
            'username', 'email', 'date_joined', 'last_login',
        ]

    def get_available_budget_info(self, obj):
        """Get available budget information"""
        return obj.get_available_budget()

    def update(self, instance, validated_data):
        """
        Override update to also persist first_name and last_name to the User model.
        The 'user' field is a HiddenField so it will not appear in validated_data by name;
        nested user data arrives under the 'user' key when source='user.*' fields are present.
        """
        # Extract nested user data (arrives keyed as 'user' because of source='user.*')
        user_data = validated_data.pop('user', {})

        # Persist profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Persist first_name / last_name back to User model
        user = instance.user
        changed = False
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
            changed = True
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
            changed = True
        if changed:
            user.save(update_fields=[k for k in user_data if k in ('first_name', 'last_name')])

        return instance
