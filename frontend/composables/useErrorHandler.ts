/**
 * Composable pour la gestion centralisée des erreurs.
 */

import type { StandardError, ParseErrorOptions } from '~/types/errors';
import {
  parseApiError,
  formatErrorsForToast,
  getFieldError,
  isValidationError,
  isAuthenticationError,
  isNetworkError,
  getErrorToastColor,
  translateFieldName,
} from '~/utils/errorHandler';

export function useErrorHandler() {
  const toast = useToast();
  const router = useRouter();

  /**
   * Gère une erreur API de manière centralisée.
   * Parse l'erreur et affiche optionnellement un toast.
   *
   * @param error - Erreur brute de l'API
   * @param options - Options de traitement
   * @returns Erreur standardisée
   */
  function handleError(
    error: any,
    options: ParseErrorOptions = {}
  ): StandardError {
    const { showToast = true, fallbackMessage } = options;

    // Parser l'erreur
    const standardError = parseApiError(error);

    // Si l'erreur a un message de fallback personnalisé, l'utiliser
    if (fallbackMessage && !standardError.fieldErrors) {
      standardError.message = fallbackMessage;
    }

    // Afficher un toast si demandé
    if (showToast) {
      showErrorToast(standardError);
    }

    // Rediriger vers login si erreur d'authentification
    if (isAuthenticationError(standardError)) {
      router.push('/login');
    }

    return standardError;
  }

  /**
   * Affiche un toast d'erreur avec le formatage approprié.
   */
  function showErrorToast(error: StandardError): void {
    const message = formatErrorsForToast(error);
    const color = getErrorToastColor(error);

    toast.add({
      title: 'Erreur',
      description: message,
      color,
      timeout: 5000,
    });
  }

  /**
   * Récupère l'erreur d'un champ spécifique.
   * Utile pour afficher les erreurs au niveau des champs de formulaire.
   */
  function getErrorForField(
    error: StandardError | null | undefined,
    fieldName: string
  ): string | null {
    return getFieldError(error, fieldName);
  }

  /**
   * Vérifie si un champ a une erreur.
   */
  function hasFieldError(
    error: StandardError | null | undefined,
    fieldName: string
  ): boolean {
    return getFieldError(error, fieldName) !== null;
  }

  /**
   * Récupère toutes les erreurs de champs sous forme de liste.
   */
  function getAllFieldErrors(error: StandardError | null | undefined): Array<{ field: string; message: string }> {
    if (!error?.fieldErrors) {
      return [];
    }

    return error.fieldErrors.map((fe) => ({
      field: fe.field,
      message: fe.messages[0],
    }));
  }

  /**
   * Formate une erreur pour affichage dans un toast.
   */
  function formatForToast(error: StandardError, maxErrors?: number): string {
    return formatErrorsForToast(error, maxErrors);
  }

  return {
    handleError,
    showErrorToast,
    getErrorForField,
    hasFieldError,
    getAllFieldErrors,
    formatForToast,
    isValidationError,
    isAuthenticationError,
    isNetworkError,
    translateFieldName,
  };
}
