/**
 * Types pour la gestion standardisée des erreurs API.
 */

/**
 * Codes d'erreur machine-readable retournés par le backend.
 */
export type ErrorCode =
  | 'VALIDATION_ERROR'
  | 'AUTHENTICATION_ERROR'
  | 'PERMISSION_DENIED'
  | 'NOT_FOUND'
  | 'METHOD_NOT_ALLOWED'
  | 'THROTTLED'
  | 'SERVER_ERROR'
  | 'NETWORK_ERROR'
  | 'UNKNOWN_ERROR';

/**
 * Catégories d'erreurs pour un traitement différencié.
 */
export type ErrorCategory = 'validation' | 'authentication' | 'authorization' | 'client' | 'server' | 'network';

/**
 * Erreur au niveau d'un champ de formulaire.
 */
export interface FieldError {
  field: string;
  messages: string[];
}

/**
 * Structure d'erreur standardisée utilisée dans toute l'application.
 */
export interface StandardError {
  /** Indique qu'une erreur est survenue */
  error: true;
  /** Code d'erreur machine-readable */
  code: ErrorCode;
  /** Message d'erreur principal user-friendly */
  message: string;
  /** Catégorie de l'erreur pour un traitement différencié */
  category: ErrorCategory;
  /** Détails des erreurs par champ (pour erreurs de validation) */
  details?: Record<string, string[]>;
  /** Erreurs de champs au format liste (pour faciliter l'affichage) */
  fieldErrors?: FieldError[];
  /** Status HTTP de la réponse (optionnel) */
  status?: number;
}

/**
 * Format de réponse d'erreur retourné par l'API Django REST Framework.
 */
export interface ApiErrorResponse {
  error: boolean;
  code: ErrorCode;
  message: string;
  details?: Record<string, string[] | Record<string, any>>;
}

/**
 * Options pour le parsing des erreurs.
 */
export interface ParseErrorOptions {
  /** Afficher automatiquement un toast */
  showToast?: boolean;
  /** Message de fallback si parsing échoue */
  fallbackMessage?: string;
}
