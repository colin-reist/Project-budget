"""
Tests pour le gestionnaire d'exceptions personnalisé.
"""

from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
)
from config.error_handlers import (
    custom_exception_handler,
    get_error_code,
    translate_error_details,
    get_error_message,
)
from config.field_labels import get_field_label


class TestFieldLabels(TestCase):
    """Tests pour la traduction des noms de champs."""

    def test_get_field_label_known_field(self):
        """Test que les champs connus sont traduits."""
        self.assertEqual(get_field_label('account'), 'Compte')
        self.assertEqual(get_field_label('destination_account'), 'Compte de destination')
        self.assertEqual(get_field_label('amount'), 'Montant')
        self.assertEqual(get_field_label('category'), 'Catégorie')

    def test_get_field_label_unknown_field(self):
        """Test que les champs inconnus sont retournés tels quels."""
        self.assertEqual(get_field_label('unknown_field'), 'unknown_field')


class TestErrorCode(TestCase):
    """Tests pour la génération des codes d'erreur."""

    def test_validation_error_code(self):
        """Test que ValidationError génère le bon code."""
        exc = ValidationError({'field': ['error']})
        self.assertEqual(get_error_code(exc), 'VALIDATION_ERROR')

    def test_authentication_error_code(self):
        """Test que NotAuthenticated génère le bon code."""
        exc = NotAuthenticated()
        self.assertEqual(get_error_code(exc), 'AUTHENTICATION_ERROR')

    def test_permission_error_code(self):
        """Test que PermissionDenied génère le bon code."""
        exc = PermissionDenied()
        self.assertEqual(get_error_code(exc), 'PERMISSION_DENIED')

    def test_not_found_error_code(self):
        """Test que NotFound génère le bon code."""
        exc = NotFound()
        self.assertEqual(get_error_code(exc), 'NOT_FOUND')


class TestTranslateErrorDetails(TestCase):
    """Tests pour la traduction des détails d'erreur."""

    def test_translate_simple_dict(self):
        """Test traduction d'un dictionnaire simple."""
        details = {
            'account': ['Ce champ est requis.'],
            'amount': ['Doit être un nombre.']
        }
        translated = translate_error_details(details)
        self.assertIn('Compte', translated)
        self.assertIn('Montant', translated)
        self.assertNotIn('account', translated)
        self.assertNotIn('amount', translated)

    def test_translate_nested_dict(self):
        """Test traduction d'un dictionnaire imbriqué."""
        details = {
            'account': {
                'name': ['Ce champ est requis.']
            }
        }
        translated = translate_error_details(details)
        self.assertIn('Compte', translated)
        self.assertIn('Nom', translated['Compte'])

    def test_translate_list(self):
        """Test traduction d'une liste d'erreurs."""
        details = ['Erreur 1', 'Erreur 2']
        translated = translate_error_details(details)
        self.assertEqual(translated, ['Erreur 1', 'Erreur 2'])

    def test_translate_string(self):
        """Test traduction d'un string."""
        details = 'Une erreur est survenue'
        translated = translate_error_details(details)
        self.assertEqual(translated, 'Une erreur est survenue')


class TestErrorMessage(TestCase):
    """Tests pour la génération des messages d'erreur."""

    def test_validation_error_message(self):
        """Test message pour erreur de validation."""
        exc = ValidationError({'field': ['error']})
        message = get_error_message(exc, 'VALIDATION_ERROR')
        self.assertIn('invalides', message.lower())

    def test_authentication_error_message(self):
        """Test message pour erreur d'authentification."""
        exc = NotAuthenticated()
        message = get_error_message(exc, 'AUTHENTICATION_ERROR')
        self.assertIn('authentification', message.lower())

    def test_permission_error_message(self):
        """Test message pour erreur de permission."""
        exc = PermissionDenied()
        message = get_error_message(exc, 'PERMISSION_DENIED')
        self.assertIn('permission', message.lower())


class DummyValidationView(APIView):
    """Vue de test qui lève une ValidationError."""
    permission_classes = []  # Désactiver l'authentification pour les tests

    def post(self, request):
        raise ValidationError({
            'account': ['Ce champ est requis.'],
            'amount': ['Doit être un nombre positif.']
        })


@override_settings(ROOT_URLCONF=__name__)
class TestCustomExceptionHandler(APITestCase):
    """Tests d'intégration pour le gestionnaire d'exception."""

    def test_validation_error_response_format(self):
        """Test que la réponse de ValidationError est au bon format."""
        factory = APIRequestFactory()
        view = DummyValidationView.as_view()

        request = factory.post('/')
        response = view(request)

        # Vérifier la structure de base
        self.assertIn('error', response.data)
        self.assertIn('code', response.data)
        self.assertIn('message', response.data)
        self.assertIn('details', response.data)

        # Vérifier les valeurs
        self.assertTrue(response.data['error'])
        self.assertEqual(response.data['code'], 'VALIDATION_ERROR')

        # Vérifier que les champs sont traduits
        details = response.data['details']
        self.assertIn('Compte', details)
        self.assertIn('Montant', details)
        self.assertNotIn('account', details)
        self.assertNotIn('amount', details)

    def test_validation_error_status_code(self):
        """Test que le status code est préservé."""
        factory = APIRequestFactory()
        view = DummyValidationView.as_view()

        request = factory.post('/')
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# Configuration minimale d'URL pour les tests
urlpatterns = []
