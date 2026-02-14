from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer, UserProfileSerializer
from .models import UserProfile

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    POST /api/auth/register/
    {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "securePassword123",
        "password2": "securePassword123",
        "first_name": "John",
        "last_name": "Doe"
    }

    Returns:
    {
        "user": {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe"
        },
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    API endpoint for user login with username/email and password.

    POST /api/auth/login/
    {
        "username": "john_doe",
        "password": "securePassword123"
    }

    Returns:
    {
        "user": {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe"
        },
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    # Try to authenticate with username first
    user = authenticate(request, username=username, password=password)

    # If authentication failed, try with email
    if user is None:
        try:
            user_obj = User.objects.get(email=username)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass

    if user is not None:
        if user.is_active:
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Account is disabled.'
            }, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({
            'error': 'Invalid credentials.'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    """
    API endpoint to get current user information.

    GET /api/auth/me/
    Headers: Authorization: Bearer <access_token>

    Returns:
    {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2026-02-03T10:00:00Z"
    }
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    API endpoint for user logout.
    Blacklists the refresh token.

    POST /api/auth/logout/
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }

    Returns:
    {
        "message": "Logout successful."
    }
    """
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'message': 'Logout successful.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Refresh token is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profile (income, available budget)
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return profile for current user only"""
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create profile for current user"""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Update current user's profile"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def setup_recurring_salary(self, request):
        """
        Créer ou mettre à jour une transaction récurrente pour le salaire mensuel.
        Propose de créer automatiquement si le salaire est défini dans le profil.
        """
        from transactions.models import Transaction
        from categories.models import Category
        from accounts.models import Account
        from decimal import Decimal
        from datetime import date
        from dateutil.relativedelta import relativedelta

        user = request.user
        profile = self.get_object()

        # Vérifier si un montant de salaire est fourni ou utiliser celui du profil
        salary_amount = request.data.get('amount')
        if salary_amount:
            salary_amount = Decimal(str(salary_amount))
        elif profile.monthly_income:
            salary_amount = profile.monthly_income
        else:
            return Response({
                'error': 'Aucun montant de salaire fourni et pas de salaire dans le profil'
            }, status=400)

        # Chercher ou créer la catégorie "Salaire"
        salary_category, created = Category.objects.get_or_create(
            user=user,
            name='Salaire',
            type='income',
            defaults={
                'icon': 'i-heroicons-banknotes',
                'color': 'green'
            }
        )

        # Chercher une transaction récurrente existante pour le salaire
        existing_transaction = Transaction.objects.filter(
            user=user,
            type='income',
            category=salary_category,
            is_recurring=True
        ).first()

        if existing_transaction:
            # Mettre à jour le montant
            existing_transaction.amount = salary_amount
            existing_transaction.save()

            return Response({
                'message': 'Transaction de salaire mise à jour',
                'transaction_id': existing_transaction.id,
                'amount': float(salary_amount),
                'created': False
            })
        else:
            # Chercher d'abord un compte courant, sinon n'importe quel compte actif
            account = (
                Account.objects.filter(user=user, is_active=True, account_type='checking').first() or
                Account.objects.filter(user=user, is_active=True).first()
            )

            if not account:
                return Response({
                    'error': 'Aucun compte actif trouvé. Créez un compte d\'abord.'
                }, status=400)

            # Calculer la date de la prochaine occurrence du salaire
            today = date.today()
            if profile.salary_day:
                # Utiliser le jour configuré dans le profil
                salary_day = min(profile.salary_day, 28)  # Max 28 pour éviter les problèmes avec février
                if today.day < salary_day:
                    # Le salaire n'est pas encore passé ce mois-ci
                    next_salary_date = date(today.year, today.month, salary_day)
                else:
                    # Le salaire est déjà passé, prendre le mois prochain
                    next_salary_date = date(today.year, today.month, salary_day) + relativedelta(months=1)
            else:
                # Pas de jour configuré, utiliser le 1er du mois prochain par défaut
                next_salary_date = date(today.year, today.month, 1) + relativedelta(months=1)

            # Créer la transaction récurrente
            transaction = Transaction.objects.create(
                user=user,
                account=account,
                category=salary_category,
                type='income',
                amount=salary_amount,
                description=request.data.get('description', 'Salaire mensuel'),
                date=next_salary_date,
                is_recurring=True,
                recurrence_frequency='monthly',
                recurrence_interval=1,
                source='web'
            )

            return Response({
                'message': 'Transaction de salaire récurrente créée',
                'transaction_id': transaction.id,
                'amount': float(salary_amount),
                'created': True
            }, status=201)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change user password

        POST /api/v1/auth/profile/change_password/
        {
            "current_password": "oldPassword123",
            "new_password": "newPassword123"
        }
        """
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        # Validate input
        if not current_password or not new_password:
            return Response({
                'error': 'Both current_password and new_password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check current password
        if not user.check_password(current_password):
            return Response({
                'error': 'Current password is incorrect.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate new password
        if len(new_password) < 8:
            return Response({
                'error': 'New password must be at least 8 characters long.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set new password
        user.set_password(new_password)
        user.save()

        return Response({
            'message': 'Password changed successfully.'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_account(self, request):
        """
        Delete user account and all associated data

        DELETE /api/v1/auth/profile/delete_account/
        {
            "password": "currentPassword123",
            "confirm": "DELETE"
        }
        """
        user = request.user
        password = request.data.get('password')
        confirm = request.data.get('confirm')

        # Validate confirmation
        if confirm != 'DELETE':
            return Response({
                'error': 'Please type DELETE to confirm account deletion.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verify password
        if not password or not user.check_password(password):
            return Response({
                'error': 'Password is incorrect.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Delete user (cascade will delete all related data)
        user.delete()

        return Response({
            'message': 'Account deleted successfully.'
        }, status=status.HTTP_200_OK)
