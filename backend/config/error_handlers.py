"""
Gestionnaire d'exceptions personnalisé pour Django REST Framework.
Standardise le format des réponses d'erreur et ajoute des codes d'erreur machine-readable.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    Throttled,
)
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from .field_labels import get_field_label


def get_error_code(exc):
    """
    Détermine le code d'erreur basé sur le type d'exception.

    Args:
        exc: L'exception levée

    Returns:
        Code d'erreur machine-readable
    """
    if isinstance(exc, ValidationError):
        return 'VALIDATION_ERROR'
    elif isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        return 'AUTHENTICATION_ERROR'
    elif isinstance(exc, PermissionDenied):
        return 'PERMISSION_DENIED'
    elif isinstance(exc, (NotFound, Http404, ObjectDoesNotExist)):
        return 'NOT_FOUND'
    elif isinstance(exc, MethodNotAllowed):
        return 'METHOD_NOT_ALLOWED'
    elif isinstance(exc, Throttled):
        return 'THROTTLED'
    else:
        return 'SERVER_ERROR'


def translate_error_details(details):
    """
    Traduit les noms de champs techniques en labels français.

    Args:
        details: Détails d'erreur de DRF (peut être dict, list, ou string)

    Returns:
        Détails d'erreur avec champs traduits
    """
    if isinstance(details, dict):
        translated = {}
        for field, errors in details.items():
            # Traduire le nom du champ
            translated_field = get_field_label(field)
            # Récursivement traduire les erreurs imbriquées
            translated[translated_field] = translate_error_details(errors)
        return translated
    elif isinstance(details, list):
        # Pour les listes d'erreurs, traduire chaque élément
        return [translate_error_details(error) for error in details]
    else:
        # Pour les strings ou autres types, retourner tel quel
        return str(details)


def get_error_message(exc, error_code):
    """
    Génère un message d'erreur user-friendly basé sur le type d'erreur.

    Args:
        exc: L'exception levée
        error_code: Code d'erreur

    Returns:
        Message d'erreur user-friendly
    """
    if error_code == 'VALIDATION_ERROR':
        return 'Les données soumises sont invalides. Veuillez corriger les erreurs.'
    elif error_code == 'AUTHENTICATION_ERROR':
        return 'Authentification requise. Veuillez vous connecter.'
    elif error_code == 'PERMISSION_DENIED':
        return "Vous n'avez pas la permission d'effectuer cette action."
    elif error_code == 'NOT_FOUND':
        return 'La ressource demandée est introuvable.'
    elif error_code == 'METHOD_NOT_ALLOWED':
        return "Cette méthode n'est pas autorisée."
    elif error_code == 'THROTTLED':
        wait = getattr(exc, 'wait', None)
        if wait:
            return f'Trop de requêtes. Veuillez réessayer dans {int(wait)} secondes.'
        return 'Trop de requêtes. Veuillez réessayer plus tard.'
    else:
        return 'Une erreur serveur est survenue. Veuillez réessayer.'


def custom_exception_handler(exc, context):
    """
    Gestionnaire d'exception personnalisé qui standardise les réponses d'erreur.

    Format de réponse :
    {
        "error": true,
        "code": "ERROR_CODE",
        "message": "Message user-friendly",
        "details": {
            "field_name": ["Erreur 1", "Erreur 2"]
        }
    }

    Args:
        exc: L'exception levée
        context: Contexte de la requête

    Returns:
        Response avec format d'erreur standardisé
    """
    # Appeler le gestionnaire par défaut de DRF pour obtenir la réponse standard
    response = exception_handler(exc, context)

    # Si DRF ne gère pas cette exception, retourner None (Django gérera)
    if response is None:
        return None

    # Déterminer le code d'erreur
    error_code = get_error_code(exc)

    # Générer le message user-friendly
    message = get_error_message(exc, error_code)

    # Traduire les détails d'erreur (noms de champs)
    details = translate_error_details(response.data) if response.data else None

    # Construire la réponse standardisée
    standardized_response = {
        'error': True,
        'code': error_code,
        'message': message,
    }

    # Ajouter les détails seulement s'ils existent
    if details:
        standardized_response['details'] = details

    return Response(standardized_response, status=response.status_code)
