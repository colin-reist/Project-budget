/**
 * Utilitaires pour parser et formater les erreurs API.
 */

import type {
  StandardError,
  ErrorCode,
  ErrorCategory,
  FieldError,
  ApiErrorResponse,
} from '~/types/errors';

/**
 * Mapping des noms de champs techniques vers des labels français.
 * Synchronisé avec backend/config/field_labels.py
 */
const FIELD_LABELS: Record<string, string> = {
  // Transaction fields
  account: 'Compte',
  destination_account: 'Compte de destination',
  category: 'Catégorie',
  amount: 'Montant',
  description: 'Description',
  date: 'Date',
  transaction_type: 'Type de transaction',
  is_planned: 'Transaction planifiée',

  // Account fields
  name: 'Nom',
  account_type: 'Type de compte',
  balance: 'Solde',
  initial_balance: 'Solde initial',
  currency: 'Devise',
  is_active: 'Compte actif',
  credit_limit: 'Limite de crédit',

  // Category fields
  category_type: 'Type de catégorie',
  color: 'Couleur',
  icon: 'Icône',
  parent: 'Catégorie parente',

  // Budget fields
  period: 'Période',
  start_date: 'Date de début',
  end_date: 'Date de fin',
  target_amount: 'Montant cible',

  // Authentication fields
  username: "Nom d'utilisateur",
  password: 'Mot de passe',
  email: 'Email',
  old_password: 'Ancien mot de passe',
  new_password: 'Nouveau mot de passe',

  // Common fields
  user: 'Utilisateur',
  created_at: 'Date de création',
  updated_at: 'Date de modification',
  non_field_errors: 'Erreur générale',
};

/**
 * Traduit un nom de champ technique en label français.
 */
export function translateFieldName(field: string): string {
  return FIELD_LABELS[field] || field;
}

/**
 * Détermine la catégorie d'une erreur basée sur son code.
 */
function getCategoryFromCode(code: ErrorCode): ErrorCategory {
  switch (code) {
    case 'VALIDATION_ERROR':
      return 'validation';
    case 'AUTHENTICATION_ERROR':
      return 'authentication';
    case 'PERMISSION_DENIED':
      return 'authorization';
    case 'NOT_FOUND':
    case 'METHOD_NOT_ALLOWED':
      return 'client';
    case 'NETWORK_ERROR':
      return 'network';
    case 'SERVER_ERROR':
    case 'THROTTLED':
    case 'UNKNOWN_ERROR':
    default:
      return 'server';
  }
}

/**
 * Convertit les détails d'erreur en liste de FieldError.
 */
function detailsToFieldErrors(details: Record<string, any>): FieldError[] {
  const fieldErrors: FieldError[] = [];

  for (const [field, value] of Object.entries(details)) {
    const translatedField = translateFieldName(field);

    if (Array.isArray(value)) {
      // Format standard: { field: ["error1", "error2"] }
      fieldErrors.push({
        field: translatedField,
        messages: value.map(String),
      });
    } else if (typeof value === 'string') {
      // Format simple: { field: "error" }
      fieldErrors.push({
        field: translatedField,
        messages: [value],
      });
    } else if (typeof value === 'object' && value !== null) {
      // Format imbriqué: { field: { nested: ["error"] } }
      // On traite récursivement
      const nestedErrors = detailsToFieldErrors(value);
      for (const nestedError of nestedErrors) {
        fieldErrors.push({
          field: `${translatedField} - ${nestedError.field}`,
          messages: nestedError.messages,
        });
      }
    }
  }

  return fieldErrors;
}

/**
 * Parse une erreur API en format StandardError.
 *
 * Gère plusieurs formats:
 * - Format nouveau (avec error, code, message, details)
 * - Format ancien DRF (avec detail ou erreurs par champ)
 * - Erreurs réseau (sans réponse)
 * - Erreurs inconnues
 */
export function parseApiError(error: any): StandardError {
  // Erreur réseau (pas de réponse du serveur)
  if (!error.response && error.message) {
    return {
      error: true,
      code: 'NETWORK_ERROR',
      message: 'Erreur de connexion. Vérifiez votre connexion internet.',
      category: 'network',
      status: 0,
    };
  }

  const response = error.response;
  const data = response?.data;
  const status = response?.status || 500;

  // Format nouveau standardisé
  if (data && typeof data === 'object' && 'error' in data && 'code' in data) {
    const apiError = data as ApiErrorResponse;
    const fieldErrors = apiError.details ? detailsToFieldErrors(apiError.details) : undefined;

    return {
      error: true,
      code: apiError.code,
      message: apiError.message,
      category: getCategoryFromCode(apiError.code),
      details: apiError.details,
      fieldErrors,
      status,
    };
  }

  // Format ancien DRF - erreur simple avec detail
  if (data && typeof data === 'object' && 'detail' in data) {
    let code: ErrorCode = 'UNKNOWN_ERROR';
    if (status === 401) code = 'AUTHENTICATION_ERROR';
    else if (status === 403) code = 'PERMISSION_DENIED';
    else if (status === 404) code = 'NOT_FOUND';
    else if (status >= 500) code = 'SERVER_ERROR';

    return {
      error: true,
      code,
      message: String(data.detail),
      category: getCategoryFromCode(code),
      status,
    };
  }

  // Format ancien DRF - erreurs de validation par champ
  if (data && typeof data === 'object' && Object.keys(data).length > 0) {
    const fieldErrors = detailsToFieldErrors(data);

    return {
      error: true,
      code: 'VALIDATION_ERROR',
      message: 'Les données soumises sont invalides. Veuillez corriger les erreurs.',
      category: 'validation',
      details: data,
      fieldErrors,
      status,
    };
  }

  // Erreur inconnue
  return {
    error: true,
    code: 'UNKNOWN_ERROR',
    message: error.message || 'Une erreur inattendue est survenue.',
    category: 'server',
    status,
  };
}

/**
 * Formate les erreurs pour affichage dans un toast.
 * Affiche jusqu'à 3 erreurs, puis indique le nombre d'erreurs restantes.
 */
export function formatErrorsForToast(error: StandardError, maxErrors: number = 3): string {
  // Si pas d'erreurs de champs, retourner le message principal
  if (!error.fieldErrors || error.fieldErrors.length === 0) {
    return error.message;
  }

  // Formater les erreurs de champs
  const lines: string[] = [];
  const errorsToShow = error.fieldErrors.slice(0, maxErrors);

  for (const fieldError of errorsToShow) {
    // Pour chaque champ, prendre le premier message
    const message = fieldError.messages[0];
    lines.push(`${fieldError.field} : ${message}`);
  }

  // Ajouter un indicateur s'il y a plus d'erreurs
  const remaining = error.fieldErrors.length - maxErrors;
  if (remaining > 0) {
    lines.push(`... et ${remaining} autre${remaining > 1 ? 's' : ''} erreur${remaining > 1 ? 's' : ''}`);
  }

  return lines.join('\n');
}

/**
 * Récupère l'erreur d'un champ spécifique.
 * Retourne le premier message d'erreur pour ce champ, ou null si aucune erreur.
 */
export function getFieldError(error: StandardError | null | undefined, fieldName: string): string | null {
  if (!error?.fieldErrors) {
    return null;
  }

  // Traduire le nom du champ pour la comparaison
  const translatedFieldName = translateFieldName(fieldName);

  // Chercher l'erreur pour ce champ
  const fieldError = error.fieldErrors.find(
    (fe) => fe.field === translatedFieldName
  );

  return fieldError?.messages[0] || null;
}

/**
 * Vérifie si une erreur est une erreur de validation.
 */
export function isValidationError(error: StandardError): boolean {
  return error.category === 'validation';
}

/**
 * Vérifie si une erreur est une erreur d'authentification.
 */
export function isAuthenticationError(error: StandardError): boolean {
  return error.category === 'authentication';
}

/**
 * Vérifie si une erreur est une erreur réseau.
 */
export function isNetworkError(error: StandardError): boolean {
  return error.category === 'network';
}

/**
 * Retourne une couleur de toast appropriée selon la catégorie d'erreur.
 */
export function getErrorToastColor(error: StandardError): 'red' | 'orange' | 'amber' {
  switch (error.category) {
    case 'validation':
      return 'orange';
    case 'authentication':
    case 'authorization':
      return 'amber';
    case 'network':
    case 'server':
    default:
      return 'red';
  }
}
