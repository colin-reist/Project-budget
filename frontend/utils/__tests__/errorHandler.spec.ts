/**
 * Tests pour l'utilitaire de gestion d'erreurs.
 */

import { describe, it, expect } from 'vitest';
import {
  parseApiError,
  translateFieldName,
  formatErrorsForToast,
  getFieldError,
  isValidationError,
  isAuthenticationError,
  isNetworkError,
} from '../errorHandler';
import type { StandardError } from '~/types/errors';

describe('translateFieldName', () => {
  it('traduit les champs connus', () => {
    expect(translateFieldName('account')).toBe('Compte');
    expect(translateFieldName('destination_account')).toBe('Compte de destination');
    expect(translateFieldName('amount')).toBe('Montant');
    expect(translateFieldName('category')).toBe('Catégorie');
  });

  it('retourne le nom original pour les champs inconnus', () => {
    expect(translateFieldName('unknown_field')).toBe('unknown_field');
  });
});

describe('parseApiError', () => {
  it('parse une erreur réseau', () => {
    const error = {
      message: 'Network Error',
    };

    const result = parseApiError(error);

    expect(result.error).toBe(true);
    expect(result.code).toBe('NETWORK_ERROR');
    expect(result.category).toBe('network');
    expect(result.message).toContain('connexion');
  });

  it('parse le nouveau format standardisé', () => {
    const error = {
      response: {
        status: 400,
        data: {
          error: true,
          code: 'VALIDATION_ERROR',
          message: 'Les données sont invalides',
          details: {
            account: ['Ce champ est requis.'],
            amount: ['Doit être un nombre positif.'],
          },
        },
      },
    };

    const result = parseApiError(error);

    expect(result.error).toBe(true);
    expect(result.code).toBe('VALIDATION_ERROR');
    expect(result.category).toBe('validation');
    expect(result.message).toBe('Les données sont invalides');
    expect(result.details).toBeDefined();
    expect(result.fieldErrors).toBeDefined();
    expect(result.fieldErrors?.length).toBe(2);
    expect(result.status).toBe(400);
  });

  it('parse le format ancien DRF avec detail', () => {
    const error = {
      response: {
        status: 404,
        data: {
          detail: 'Non trouvé.',
        },
      },
    };

    const result = parseApiError(error);

    expect(result.error).toBe(true);
    expect(result.code).toBe('NOT_FOUND');
    expect(result.category).toBe('client');
    expect(result.message).toBe('Non trouvé.');
    expect(result.status).toBe(404);
  });

  it('parse le format ancien DRF avec erreurs par champ', () => {
    const error = {
      response: {
        status: 400,
        data: {
          account: ['Ce champ est requis.'],
          amount: ['Entrez un nombre valide.'],
        },
      },
    };

    const result = parseApiError(error);

    expect(result.error).toBe(true);
    expect(result.code).toBe('VALIDATION_ERROR');
    expect(result.category).toBe('validation');
    expect(result.fieldErrors).toBeDefined();
    expect(result.fieldErrors?.length).toBe(2);

    // Vérifier que les champs sont traduits
    const accountError = result.fieldErrors?.find((fe) => fe.field === 'Compte');
    expect(accountError).toBeDefined();
    expect(accountError?.messages[0]).toBe('Ce champ est requis.');

    const amountError = result.fieldErrors?.find((fe) => fe.field === 'Montant');
    expect(amountError).toBeDefined();
    expect(amountError?.messages[0]).toBe('Entrez un nombre valide.');
  });

  it('parse une erreur d\'authentification', () => {
    const error = {
      response: {
        status: 401,
        data: {
          detail: 'Identifiants invalides.',
        },
      },
    };

    const result = parseApiError(error);

    expect(result.code).toBe('AUTHENTICATION_ERROR');
    expect(result.category).toBe('authentication');
  });

  it('parse une erreur serveur', () => {
    const error = {
      response: {
        status: 500,
        data: {
          detail: 'Erreur serveur interne.',
        },
      },
    };

    const result = parseApiError(error);

    expect(result.code).toBe('SERVER_ERROR');
    expect(result.category).toBe('server');
  });

  it('gère les erreurs imbriquées', () => {
    const error = {
      response: {
        status: 400,
        data: {
          account: {
            name: ['Ce champ est requis.'],
          },
        },
      },
    };

    const result = parseApiError(error);

    expect(result.fieldErrors).toBeDefined();
    expect(result.fieldErrors?.length).toBeGreaterThan(0);
    expect(result.fieldErrors?.[0].field).toContain('Compte');
    expect(result.fieldErrors?.[0].field).toContain('Nom');
  });
});

describe('formatErrorsForToast', () => {
  it('formate une erreur simple sans champs', () => {
    const error: StandardError = {
      error: true,
      code: 'SERVER_ERROR',
      message: 'Erreur serveur',
      category: 'server',
    };

    const result = formatErrorsForToast(error);

    expect(result).toBe('Erreur serveur');
  });

  it('formate des erreurs de champs', () => {
    const error: StandardError = {
      error: true,
      code: 'VALIDATION_ERROR',
      message: 'Erreurs de validation',
      category: 'validation',
      fieldErrors: [
        { field: 'Compte', messages: ['Ce champ est requis.'] },
        { field: 'Montant', messages: ['Doit être positif.'] },
      ],
    };

    const result = formatErrorsForToast(error);

    expect(result).toContain('Compte : Ce champ est requis.');
    expect(result).toContain('Montant : Doit être positif.');
  });

  it('limite le nombre d\'erreurs affichées', () => {
    const error: StandardError = {
      error: true,
      code: 'VALIDATION_ERROR',
      message: 'Erreurs de validation',
      category: 'validation',
      fieldErrors: [
        { field: 'Champ1', messages: ['Erreur 1'] },
        { field: 'Champ2', messages: ['Erreur 2'] },
        { field: 'Champ3', messages: ['Erreur 3'] },
        { field: 'Champ4', messages: ['Erreur 4'] },
        { field: 'Champ5', messages: ['Erreur 5'] },
      ],
    };

    const result = formatErrorsForToast(error, 3);

    expect(result).toContain('Champ1');
    expect(result).toContain('Champ2');
    expect(result).toContain('Champ3');
    expect(result).toContain('2 autres erreurs');
    expect(result).not.toContain('Champ4');
  });
});

describe('getFieldError', () => {
  const error: StandardError = {
    error: true,
    code: 'VALIDATION_ERROR',
    message: 'Erreurs de validation',
    category: 'validation',
    fieldErrors: [
      { field: 'Compte', messages: ['Ce champ est requis.', 'Second message'] },
      { field: 'Montant', messages: ['Doit être positif.'] },
    ],
  };

  it('retourne l\'erreur d\'un champ existant', () => {
    const result = getFieldError(error, 'account');
    expect(result).toBe('Ce champ est requis.');
  });

  it('retourne null pour un champ sans erreur', () => {
    const result = getFieldError(error, 'description');
    expect(result).toBeNull();
  });

  it('retourne null si pas d\'erreur', () => {
    const result = getFieldError(null, 'account');
    expect(result).toBeNull();
  });

  it('retourne null si pas de fieldErrors', () => {
    const simpleError: StandardError = {
      error: true,
      code: 'SERVER_ERROR',
      message: 'Erreur',
      category: 'server',
    };
    const result = getFieldError(simpleError, 'account');
    expect(result).toBeNull();
  });
});

describe('isValidationError', () => {
  it('identifie une erreur de validation', () => {
    const error: StandardError = {
      error: true,
      code: 'VALIDATION_ERROR',
      message: 'Erreur',
      category: 'validation',
    };
    expect(isValidationError(error)).toBe(true);
  });

  it('rejette une erreur non-validation', () => {
    const error: StandardError = {
      error: true,
      code: 'SERVER_ERROR',
      message: 'Erreur',
      category: 'server',
    };
    expect(isValidationError(error)).toBe(false);
  });
});

describe('isAuthenticationError', () => {
  it('identifie une erreur d\'authentification', () => {
    const error: StandardError = {
      error: true,
      code: 'AUTHENTICATION_ERROR',
      message: 'Erreur',
      category: 'authentication',
    };
    expect(isAuthenticationError(error)).toBe(true);
  });

  it('rejette une erreur non-authentification', () => {
    const error: StandardError = {
      error: true,
      code: 'VALIDATION_ERROR',
      message: 'Erreur',
      category: 'validation',
    };
    expect(isAuthenticationError(error)).toBe(false);
  });
});

describe('isNetworkError', () => {
  it('identifie une erreur réseau', () => {
    const error: StandardError = {
      error: true,
      code: 'NETWORK_ERROR',
      message: 'Erreur',
      category: 'network',
    };
    expect(isNetworkError(error)).toBe(true);
  });

  it('rejette une erreur non-réseau', () => {
    const error: StandardError = {
      error: true,
      code: 'VALIDATION_ERROR',
      message: 'Erreur',
      category: 'validation',
    };
    expect(isNetworkError(error)).toBe(false);
  });
});
