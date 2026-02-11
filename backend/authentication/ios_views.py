"""
Vues pour l'intégration iOS (endpoint transaction) et gestion des alertes/tokens.
"""
from datetime import date
from decimal import Decimal, InvalidOperation

from rest_framework import status as http_status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .api_token import APIToken, PendingAlert
from .rate_limit import check_rate_limit
from .token_auth import APITokenAuthentication
from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction


# =============================================================================
# Endpoint iOS — Transaction
# =============================================================================

@api_view(['POST'])
@authentication_classes([APITokenAuthentication])
@permission_classes([IsAuthenticated])
def ios_create_transaction(request):
    """
    POST /api/v1/ios/transaction/
    Body: { "amount": 12.50, "label": "Café + sandwich", "category": "Alimentation" }

    Réponses :
    - 201 : Transaction créée
    - 207 : Transaction créée mais catégorie inconnue
    - 401 : Token invalide
    - 422 : Champ manquant ou montant invalide
    """
    user = request.user
    api_token = request.auth

    # Rate limiting
    check_rate_limit(api_token.id)

    # Extraction et validation
    amount_raw = request.data.get('amount')
    label = request.data.get('label', '')
    category_name = request.data.get('category', '')

    if amount_raw is None:
        return Response(
            {'error': 'Le montant est requis.'},
            status=http_status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    try:
        amount = Decimal(str(amount_raw))
        if amount <= 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        return Response(
            {'error': 'Montant invalide.'},
            status=http_status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    if not label:
        return Response(
            {'error': 'Le label est requis.'},
            status=http_status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    # Compte par défaut (premier compte courant actif)
    default_account = Account.objects.filter(
        user=user, is_active=True, account_type='checking'
    ).first()
    if not default_account:
        default_account = Account.objects.filter(user=user, is_active=True).first()
    if not default_account:
        return Response(
            {'error': 'Aucun compte actif trouvé.'},
            status=http_status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    # Recherche de catégorie
    category = None
    source = 'ios'
    multi_status = False

    if category_name:
        category = Category.objects.filter(
            user=user,
            name__iexact=category_name,
            type='expense',
            is_active=True
        ).first()

        if not category:
            source = 'ios_uncategorized'
            multi_status = True

    # Création de la transaction
    transaction = Transaction.objects.create(
        user=user,
        account=default_account,
        category=category,
        type='expense',
        amount=amount,
        description=label,
        date=date.today(),
        source=source,
    )

    # Alerte si catégorie inconnue
    if multi_status:
        PendingAlert.objects.create(
            user=user,
            type='unknown_category',
            payload={
                'transaction_id': transaction.id,
                'category_name': category_name,
                'amount': str(amount),
                'label': label,
            }
        )

    response_data = {
        'id': transaction.id,
        'amount': str(transaction.amount),
        'description': transaction.description,
        'category': category.name if category else None,
        'date': str(transaction.date),
        'source': source,
    }

    if multi_status:
        response_data['warning'] = (
            f'Catégorie "{category_name}" non trouvée. '
            f'Transaction créée sans catégorie.'
        )
        return Response(response_data, status=207)

    return Response(response_data, status=http_status.HTTP_201_CREATED)


# =============================================================================
# Endpoints Alertes (auth JWT classique)
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alert_list(request):
    """Liste des alertes non vues pour l'utilisateur."""
    alerts = PendingAlert.objects.filter(user=request.user, seen=False)
    data = [
        {
            'id': a.id,
            'type': a.type,
            'payload': a.payload,
            'seen': a.seen,
            'created_at': a.created_at.isoformat(),
        }
        for a in alerts
    ]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alert_count(request):
    """Nombre d'alertes non vues."""
    count = PendingAlert.objects.filter(user=request.user, seen=False).count()
    return Response({'count': count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def alert_dismiss(request, alert_id):
    """Marquer une alerte comme vue."""
    try:
        alert = PendingAlert.objects.get(id=alert_id, user=request.user)
    except PendingAlert.DoesNotExist:
        return Response(
            {'error': 'Alerte non trouvée.'},
            status=http_status.HTTP_404_NOT_FOUND
        )
    alert.seen = True
    alert.save(update_fields=['seen'])
    return Response({'status': 'ok'})


# =============================================================================
# Endpoints Tokens API (auth JWT classique)
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def token_list(request):
    """Liste des API tokens de l'utilisateur."""
    tokens = APIToken.objects.filter(user=request.user)
    data = [
        {
            'id': t.id,
            'name': t.name,
            'created_at': t.created_at.isoformat(),
            'last_used': t.last_used.isoformat() if t.last_used else None,
            'is_active': t.is_active,
        }
        for t in tokens
    ]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def token_create(request):
    """Créer un nouveau API token. Le token brut est retourné une seule fois."""
    name = request.data.get('name', '')
    if not name:
        return Response(
            {'error': 'Le nom du token est requis.'},
            status=http_status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    api_token = APIToken(user=request.user, name=name)
    api_token.save()

    return Response(
        {
            'id': api_token.id,
            'name': api_token.name,
            'token': api_token.token,  # Affiché une seule fois
            'created_at': api_token.created_at.isoformat(),
        },
        status=http_status.HTTP_201_CREATED
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def token_delete(request, token_id):
    """Révoquer (supprimer) un API token."""
    try:
        api_token = APIToken.objects.get(id=token_id, user=request.user)
    except APIToken.DoesNotExist:
        return Response(
            {'error': 'Token non trouvé.'},
            status=http_status.HTTP_404_NOT_FOUND
        )
    api_token.delete()
    return Response(status=http_status.HTTP_204_NO_CONTENT)
