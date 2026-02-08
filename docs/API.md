# Documentation API - Application de Suivi de Budget

## Vue d'ensemble

API RESTful pour gérer les comptes, transactions, budgets et authentification de l'application de suivi de budget.

**Base URL :** `http://localhost:8000/api/v1`  
**Format :** JSON  
**Authentification :** JWT (JSON Web Token)

---

## Table des matières

1. [Authentification](#authentification)
2. [Comptes bancaires](#comptes-bancaires)
3. [Transactions](#transactions)
4. [Catégories](#catégories)
5. [Budgets](#budgets)
6. [Récurrence](#récurrence)
7. [Statistiques](#statistiques)
8. [Tokens API](#tokens-api)
9. [Codes d'erreur](#codes-derreur)

---

## Authentification

### 1. Enregistrement (Register)

Créer un nouveau compte utilisateur.

**Endpoint :** `POST /auth/register`  
**Auth requise :** Non

**Body :**
```json
{
  "email": "user@example.com",
  "username": "john_doe"
}
```

**Réponse (201 Created) :**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "created_at": "2026-02-03T10:00:00Z"
}
```

---

### 2. Enregistrer une Passkey (WebAuthn)

Enregistrer une clé d'authentification WebAuthn.

**Endpoint :** `POST /auth/webauthn/register/begin`  
**Auth requise :** Non (session temporaire après register)

**Body :**
```json
{
  "user_id": 1
}
```

**Réponse (200 OK) :**
```json
{
  "challenge": "base64_encoded_challenge",
  "rp": {
    "name": "Budget Tracker",
    "id": "localhost"
  },
  "user": {
    "id": "user_1",
    "name": "user@example.com",
    "displayName": "john_doe"
  },
  "pubKeyCredParams": [
    {"type": "public-key", "alg": -7},
    {"type": "public-key", "alg": -257}
  ],
  "timeout": 60000,
  "attestation": "none"
}
```

**Endpoint :** `POST /auth/webauthn/register/complete`

**Body :**
```json
{
  "credential": {
    "id": "credential_id",
    "rawId": "base64_raw_id",
    "response": {
      "attestationObject": "base64_attestation",
      "clientDataJSON": "base64_client_data"
    },
    "type": "public-key"
  },
  "device_name": "Proton Pass"
}
```

**Réponse (201 Created) :**
```json
{
  "success": true,
  "message": "Passkey enregistrée avec succès"
}
```

---

### 3. Connexion avec Passkey

Authentifier un utilisateur avec WebAuthn.

**Endpoint :** `POST /auth/webauthn/login/begin`  
**Auth requise :** Non

**Body :**
```json
{
  "email": "user@example.com"
}
```

**Réponse (200 OK) :**
```json
{
  "challenge": "base64_encoded_challenge",
  "timeout": 60000,
  "rpId": "localhost",
  "allowCredentials": [
    {
      "type": "public-key",
      "id": "base64_credential_id"
    }
  ]
}
```

**Endpoint :** `POST /auth/webauthn/login/complete`

**Body :**
```json
{
  "credential": {
    "id": "credential_id",
    "rawId": "base64_raw_id",
    "response": {
      "authenticatorData": "base64_auth_data",
      "clientDataJSON": "base64_client_data",
      "signature": "base64_signature"
    },
    "type": "public-key"
  }
}
```

**Réponse (200 OK) :**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe"
  }
}
```

---

### 4. Rafraîchir le token

Obtenir un nouveau access token avec le refresh token.

**Endpoint :** `POST /auth/token/refresh`  
**Auth requise :** Non

**Body :**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Réponse (200 OK) :**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## Comptes bancaires

### 1. Lister les comptes

Obtenir tous les comptes de l'utilisateur.

**Endpoint :** `GET /accounts`  
**Auth requise :** Oui

**Réponse (200 OK) :**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "name": "Compte Courant",
      "account_type": {
        "id": 1,
        "name": "Compte courant"
      },
      "balance": 1250.50,
      "currency": "EUR",
      "created_at": "2026-01-01T12:00:00Z",
      "updated_at": "2026-02-03T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Livret A",
      "account_type": {
        "id": 2,
        "name": "Compte épargne"
      },
      "balance": 5000.00,
      "currency": "EUR",
      "created_at": "2026-01-01T12:00:00Z",
      "updated_at": "2026-02-03T10:00:00Z"
    }
  ]
}
```

---

### 2. Créer un compte

Créer un nouveau compte bancaire.

**Endpoint :** `POST /accounts`  
**Auth requise :** Oui

**Body :**
```json
{
  "name": "Compte joint",
  "account_type_id": 4,
  "balance": 0.00,
  "currency": "EUR"
}
```

**Réponse (201 Created) :**
```json
{
  "id": 3,
  "name": "Compte joint",
  "account_type": {
    "id": 4,
    "name": "Compte joint"
  },
  "balance": 0.00,
  "currency": "EUR",
  "created_at": "2026-02-03T10:30:00Z",
  "updated_at": "2026-02-03T10:30:00Z"
}
```

---

### 3. Détails d'un compte

Obtenir les détails d'un compte spécifique.

**Endpoint :** `GET /accounts/{id}`  
**Auth requise :** Oui

**Réponse (200 OK) :**
```json
{
  "id": 1,
  "name": "Compte Courant",
  "account_type": {
    "id": 1,
    "name": "Compte courant",
    "description": "Compte bancaire pour les opérations courantes"
  },
  "balance": 1250.50,
  "currency": "EUR",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-02-03T10:00:00Z",
  "transaction_count": 45,
  "last_transaction_date": "2026-02-02T15:30:00Z"
}
```

---

### 4. Modifier un compte

Mettre à jour les informations d'un compte.

**Endpoint :** `PATCH /accounts/{id}`  
**Auth requise :** Oui

**Body :**
```json
{
  "name": "Compte Courant Principal"
}
```

**Réponse (200 OK) :**
```json
{
  "id": 1,
  "name": "Compte Courant Principal",
  "account_type": {
    "id": 1,
    "name": "Compte courant"
  },
  "balance": 1250.50,
  "currency": "EUR",
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-02-03T11:00:00Z"
}
```

---

### 5. Supprimer un compte

Supprimer un compte bancaire.

**Endpoint :** `DELETE /accounts/{id}`  
**Auth requise :** Oui

**Réponse (204 No Content)**

---

## Transactions

### 1. Lister les transactions

Obtenir toutes les transactions avec filtres optionnels.

**Endpoint :** `GET /transactions`  
**Auth requise :** Oui

**Paramètres de requête :**
- `account_id` (optionnel) : Filtrer par compte
- `category_id` (optionnel) : Filtrer par catégorie
- `start_date` (optionnel) : Date de début (YYYY-MM-DD)
- `end_date` (optionnel) : Date de fin (YYYY-MM-DD)
- `min_amount` (optionnel) : Montant minimum
- `max_amount` (optionnel) : Montant maximum
- `search` (optionnel) : Recherche dans la description
- `page` (optionnel) : Numéro de page (défaut: 1)
- `page_size` (optionnel) : Résultats par page (défaut: 50, max: 100)

**Exemple :** `GET /transactions?account_id=1&start_date=2026-02-01&page=1&page_size=20`

**Réponse (200 OK) :**
```json
{
  "count": 156,
  "next": "http://localhost:8000/api/v1/transactions?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "account": {
        "id": 1,
        "name": "Compte Courant"
      },
      "category": {
        "id": 3,
        "name": "Alimentation",
        "color": "#4CAF50",
        "icon": "shopping-cart"
      },
      "amount": -45.80,
      "description": "Courses Carrefour",
      "transaction_date": "2026-02-02",
      "is_recurring": false,
      "recurrence_rule": null,
      "created_at": "2026-02-02T18:30:00Z",
      "updated_at": "2026-02-02T18:30:00Z"
    }
  ]
}
```

---

### 2. Créer une transaction

Ajouter une nouvelle transaction.

**Endpoint :** `POST /transactions`  
**Auth requise :** Oui

**Body :**
```json
{
  "account_id": 1,
  "category_id": 3,
  "amount": -45.80,
  "description": "Courses Carrefour",
  "transaction_date": "2026-02-02",
  "is_recurring": false
}
```

**Réponse (201 Created) :**
```json
{
  "id": 1,
  "account": {
    "id": 1,
    "name": "Compte Courant"
  },
  "category": {
    "id": 3,
    "name": "Alimentation",
    "color": "#4CAF50",
    "icon": "shopping-cart"
  },
  "amount": -45.80,
  "description": "Courses Carrefour",
  "transaction_date": "2026-02-02",
  "is_recurring": false,
  "recurrence_rule": null,
  "created_at": "2026-02-02T18:30:00Z",
  "updated_at": "2026-02-02T18:30:00Z"
}
```

---

### 3. Créer une transaction récurrente

Ajouter une transaction avec règle de récurrence.

**Endpoint :** `POST /transactions`  
**Auth requise :** Oui

**Body :**
```json
{
  "account_id": 1,
  "category_id": 5,
  "amount": -800.00,
  "description": "Loyer",
  "transaction_date": "2026-02-01",
  "is_recurring": true,
  "recurrence_rule": {
    "frequency": "monthly",
    "interval": 1,
    "start_date": "2026-02-01",
    "end_date": null
  }
}
```

**Réponse (201 Created) :**
```json
{
  "id": 2,
  "account": {
    "id": 1,
    "name": "Compte Courant"
  },
  "category": {
    "id": 5,
    "name": "Logement",
    "color": "#FF5722",
    "icon": "home"
  },
  "amount": -800.00,
  "description": "Loyer",
  "transaction_date": "2026-02-01",
  "is_recurring": true,
  "recurrence_rule": {
    "id": 1,
    "frequency": "monthly",
    "interval": 1,
    "start_date": "2026-02-01",
    "end_date": null
  },
  "created_at": "2026-02-03T12:00:00Z",
  "updated_at": "2026-02-03T12:00:00Z"
}
```

---

### 4. Détails d'une transaction

Obtenir les détails d'une transaction.

**Endpoint :** `GET /transactions/{id}`  
**Auth requise :** Oui

**Réponse (200 OK) :**
```json
{
  "id": 1,
  "account": {
    "id": 1,
    "name": "Compte Courant",
    "balance": 1204.70
  },
  "category": {
    "id": 3,
    "name": "Alimentation",
    "color": "#4CAF50",
    "icon": "shopping-cart",
    "type": "expense"
  },
  "amount": -45.80,
  "description": "Courses Carrefour",
  "transaction_date": "2026-02-02",
  "is_recurring": false,
  "recurrence_rule": null,
  "created_at": "2026-02-02T18:30:00Z",
  "updated_at": "2026-02-02T18:30:00Z"
}
```

---

### 5. Modifier une transaction

Mettre à jour une transaction existante.

**Endpoint :** `PATCH /transactions/{id}`  
**Auth requise :** Oui

**Body :**
```json
{
  "amount": -48.50,
  "description": "Courses Carrefour + essence"
}
```

**Réponse (200 OK) :**
```json
{
  "id": 1,
  "account": {
    "id": 1,
    "name": "Compte Courant"
  },
  "category": {
    "id": 3,
    "name": "Alimentation",
    "color": "#4CAF50",
    "icon": "shopping-cart"
  },
  "amount": -48.50,
  "description": "Courses Carrefour + essence",
  "transaction_date": "2026-02-02",
  "is_recurring": false,
  "recurrence_rule": null,
  "created_at": "2026-02-02T18:30:00Z",
  "updated_at": "2026-02-03T14:00:00Z"
}
```

---

### 6. Supprimer une transaction

Supprimer une transaction.

**Endpoint :** `DELETE /transactions/{id}`  
**Auth requise :** Oui

**Réponse (204 No Content)**

---

### 7. Rechercher des transactions

Recherche avancée dans les transactions.

**Endpoint :** `GET /transactions/search`  
**Auth requise :** Oui

**Paramètres de requête :**
- `q` (requis) : Terme de recherche

**Exemple :** `GET /transactions/search?q=carrefour`

**Réponse (200 OK) :**
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "account": {
        "id": 1,
        "name": "Compte Courant"
      },
      "category": {
        "id": 3,
        "name": "Alimentation",
        "color": "#4CAF50",
        "icon": "shopping-cart"
      },
      "amount": -48.50,
      "description": "Courses Carrefour + essence",
      "transaction_date": "2026-02-02",
      "is_recurring": false
    }
  ]
}
```

---

## Catégories

### 1. Lister les catégories

Obtenir toutes les catégories (globales + personnalisées).

**Endpoint :** `GET /categories`  
**Auth requise :** Oui

**Paramètres de requête :**
- `type` (optionnel) : Filtrer par type ('income' ou 'expense')

**Réponse (200 OK) :**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "name": "Salaire",
      "color": "#2196F3",
      "icon": "briefcase",
      "type": "income",
      "is_custom": false,
      "created_at": "2026-01-01T00:00:00Z"
    },
    {
      "id": 3,
      "name": "Alimentation",
      "color": "#4CAF50",
      "icon": "shopping-cart",
      "type": "expense",
      "is_custom": false,
      "created_at": "2026-01-01T00:00:00Z"
    },
    {
      "id": 15,
      "name": "Matériel Musique",
      "color": "#9C27B0",
      "icon": "music",
      "type": "expense",
      "is_custom": true,
      "created_at": "2026-01-15T10:00:00Z"
    }
  ]
}
```

---

### 2. Créer une catégorie

Créer une catégorie personnalisée.

**Endpoint :** `POST /categories`  
**Auth requise :** Oui

**Body :**
```json
{
  "name": "Matériel Musique",
  "color": "#9C27B0",
  "icon": "music",
  "type": "expense"
}
```

**Réponse (201 Created) :**
```json
{
  "id": 15,
  "name": "Matériel Musique",
  "color": "#9C27B0",
  "icon": "music",
  "type": "expense",
  "is_custom": true,
  "created_at": "2026-01-15T10:00:00Z"
}
```

---

### 3. Modifier une catégorie

Mettre à jour une catégorie personnalisée.

**Endpoint :** `PATCH /categories/{id}`  
**Auth requise :** Oui

**Body :**
```json
{
  "color": "#673AB7"
}
```

**Réponse (200 OK) :**
```json
{
  "id": 15,
  "name": "Matériel Musique",
  "color": "#673AB7",
  "icon": "music",
  "type": "expense",
  "is_custom": true,
  "created_at": "2026-01-15T10:00:00Z"
}
```

---

### 4. Supprimer une catégorie

Supprimer une catégorie personnalisée.

**Endpoint :** `DELETE /categories/{id}`  
**Auth requise :** Oui

**Note :** Les catégories globales ne peuvent pas être supprimées.

**Réponse (204 No Content)**

---

## Budgets

### 1. Lister les budgets

Obtenir tous les budgets de l'utilisateur.

**Endpoint :** `GET /budgets`  
**Auth requise :** Oui

**Réponse (200 OK) :**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "name": "Matériel Sono",
      "category": {
        "id": 15,
        "name": "Matériel Musique",
        "color": "#9C27B0"
      },
      "target_amount": 500.00,
      "current_amount": 120.00,
      "target_date": "2026-06-30",
      "monthly_target": 95.00,
      "progress_percentage": 24.0,
      "days_remaining": 147,
      "created_at": "2026-01-01T12:00:00Z",
      "updated_at": "2026-02-03T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Vacances été",
      "category": null,
      "target_amount": 2000.00,
      "current_amount": 450.00,
      "target_date": "2026-07-01",
      "monthly_target": 387.50,
      "progress_percentage": 22.5,
      "days_remaining": 148,
      "created_at": "2026-01-10T12:00:00Z",
      "updated_at": "2026-02-03T10:00:00Z"
    }
  ]
}
```

---

### 2. Créer un budget

Créer un nouvel objectif de budget.

**Endpoint :** `POST /budgets`  
**Auth requise :** Oui

**Body :**
```json
{
  "name": "Matériel Sono",
  "category_id": 15,
  "target_amount": 500.00,
  "current_amount": 0.00,
  "target_date": "2026-06-30"
}
```

**Réponse (201 Created) :**
```json
{
  "id": 1,
  "name": "Matériel Sono",
  "category": {
    "id": 15,
    "name": "Matériel Musique",
    "color": "#9C27B0"
  },
  "target_amount": 500.00,
  "current_amount": 0.00,
  "target_date": "2026-06-30",
  "monthly_target": 100.00,
  "progress_percentage": 0.0,
  "days_remaining": 147,
  "created_at": "2026-02-03T15:00:00Z",
  "updated_at": "2026-02-03T15:00:00Z"
}
```

---

### 3. Mettre à jour un budget

Modifier un budget existant.

**Endpoint :** `PATCH /budgets/{id}`  
**Auth requise :** Oui

**Body :**
```json
{
  "current_amount": 120.00
}
```

**Réponse (200 OK) :**
```json
{
  "id": 1,
  "name": "Matériel Sono",
  "category": {
    "id": 15,
    "name": "Matériel Musique",
    "color": "#9C27B0"
  },
  "target_amount": 500.00,
  "current_amount": 120.00,
  "target_date": "2026-06-30",
  "monthly_target": 95.00,
  "progress_percentage": 24.0,
  "days_remaining": 147,
  "created_at": "2026-01-01T12:00:00Z",
  "updated_at": "2026-02-03T16:00:00Z"
}
```

---

### 4. Supprimer un budget

Supprimer un budget.

**Endpoint :** `DELETE /budgets/{id}`  
**Auth requise :** Oui

**Réponse (204 No Content)**

---

## Récurrence

### 1. Lister les règles de récurrence

Obtenir toutes les règles de récurrence actives.

**Endpoint :** `GET /recurrence-rules`  
**Auth requise :** Oui

**Réponse (200 OK) :**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "frequency": "monthly",
      "interval": 1,
      "start_date": "2026-02-01",
      "end_date": null,
      "next_occurrence": "2026-03-01",
      "transaction": {
        "id": 2,
        "description": "Loyer",
        "amount": -800.00
      }
    }
  ]
}
```

---

### 2. Modifier une règle de récurrence

Mettre à jour une règle de récurrence.

**Endpoint :** `PATCH /recurrence-rules/{id}`  
**Auth requise :** Oui

**Body :**
```json
{
  "end_date": "2026-12-31"
}
```

**Réponse (200 OK) :**
```json
{
  "id": 1,
  "frequency": "monthly",
  "interval": 1,
  "start_date": "2026-02-01",
  "end_date": "2026-12-31",
  "next_occurrence": "2026-03-01"
}
```

---

## Statistiques

### 1. Vue d'ensemble (Dashboard)

Obtenir les statistiques globales.

**Endpoint :** `GET /stats/overview`  
**Auth requise :** Oui

**Paramètres de requête :**
- `period` (optionnel) : 'week', 'month', 'year' (défaut: 'month')

**Réponse (200 OK) :**
```json
{
  "total_balance": 6250.50,
  "accounts_count": 2,
  "budgets": {
    "active_count": 2,
    "total_target": 2500.00,
    "total_saved": 570.00,
    "average_progress": 22.8
  },
  "current_period": {
    "period": "month",
    "start_date": "2026-02-01",
    "end_date": "2026-02-28",
    "total_income": 2500.00,
    "total_expenses": -1345.30,
    "net": 1154.70,
    "transactions_count": 45
  },
  "top_categories": [
    {
      "category": "Alimentation",
      "amount": -456.80,
      "percentage": 34.0
    },
    {
      "category": "Transport",
      "amount": -234.50,
      "percentage": 17.4
    }
  ]
}
```

---

### 2. Dépenses par catégorie

Obtenir la répartition des dépenses par catégorie.

**Endpoint :** `GET /stats/expenses-by-category`  
**Auth requise :** Oui

**Paramètres de requête :**
- `start_date` (optionnel) : Date de début (YYYY-MM-DD)
- `end_date` (optionnel) : Date de fin (YYYY-MM-DD)
- `account_id` (optionnel) : Filtrer par compte

**Réponse (200 OK) :**
```json
{
  "period": {
    "start_date": "2026-02-01",
    "end_date": "2026-02-28"
  },
  "total_expenses": -1345.30,
  "categories": [
    {
      "id": 3,
      "name": "Alimentation",
      "color": "#4CAF50",
      "amount": -456.80,
      "percentage": 34.0,
      "transactions_count": 12
    },
    {
      "id": 4,
      "name": "Transport",
      "color": "#FF9800",
      "amount": -234.50,
      "percentage": 17.4,
      "transactions_count": 8
    }
  ]
}
```

---

### 3. Évolution du solde

Obtenir l'évolution du solde des comptes dans le temps.

**Endpoint :** `GET /stats/balance-evolution`  
**Auth requise :** Oui

**Paramètres de requête :**
- `account_id` (optionnel) : ID du compte (si omis, tous les comptes)
- `start_date` (requis) : Date de début (YYYY-MM-DD)
- `end_date` (requis) : Date de fin (YYYY-MM-DD)
- `granularity` (optionnel) : 'day', 'week', 'month' (défaut: 'day')

**Réponse (200 OK) :**
```json
{
  "account_id": 1,
  "account_name": "Compte Courant",
  "period": {
    "start_date": "2026-01-01",
    "end_date": "2026-02-03"
  },
  "granularity": "day",
  "data": [
    {
      "date": "2026-01-01",
      "balance": 1000.00
    },
    {
      "date": "2026-01-02",
      "balance": 955.20
    },
    {
      "date": "2026-02-03",
      "balance": 1250.50
    }
  ]
}
```

---

## Tokens API

### 1. Lister les tokens API

Obtenir tous les tokens API de l'utilisateur.

**Endpoint :** `GET /api-tokens`  
**Auth requise :** Oui (JWT)

**Réponse (200 OK) :**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "name": "iPhone Personnel",
      "last_used": "2026-02-03T09:30:00Z",
      "is_active": true,
      "created_at": "2026-01-15T10:00:00Z",
      "expires_at": null
    },
    {
      "id": 2,
      "name": "Script Python",
      "last_used": null,
      "is_active": false,
      "created_at": "2026-01-20T14:00:00Z",
      "expires_at": "2026-07-20T14:00:00Z"
    }
  ]
}
```

---

### 2. Créer un token API

Générer un nouveau token pour accès API.

**Endpoint :** `POST /api-tokens`  
**Auth requise :** Oui (JWT)

**Body :**
```json
{
  "name": "iPhone Personnel",
  "expires_at": null
}
```

**Réponse (201 Created) :**
```json
{
  "id": 1,
  "name": "iPhone Personnel",
  "token": "apt_1a2b3c4d5e6f7g8h9i0j",
  "is_active": true,
  "created_at": "2026-02-03T10:00:00Z",
  "expires_at": null,
  "warning": "Copiez ce token maintenant, il ne sera plus visible"
}
```

**Note :** Le token complet n'est visible qu'à la création.

---

### 3. Révoquer un token API

Désactiver un token API.

**Endpoint :** `DELETE /api-tokens/{id}`  
**Auth requise :** Oui (JWT)

**Réponse (204 No Content)**

---

## Codes d'erreur

### Codes HTTP standards

| Code | Signification                  | Description                                      |
|------|--------------------------------|--------------------------------------------------|
| 200  | OK                             | Requête réussie                                  |
| 201  | Created                        | Ressource créée avec succès                      |
| 204  | No Content                     | Requête réussie, pas de contenu à retourner      |
| 400  | Bad Request                    | Données invalides dans la requête                |
| 401  | Unauthorized                   | Authentification requise ou token invalide       |
| 403  | Forbidden                      | Accès refusé à cette ressource                   |
| 404  | Not Found                      | Ressource non trouvée                            |
| 409  | Conflict                       | Conflit (ex: email déjà utilisé)                 |
| 422  | Unprocessable Entity           | Validation échouée                               |
| 429  | Too Many Requests              | Limite de taux dépassée                          |
| 500  | Internal Server Error          | Erreur serveur                                   |

---

### Format des erreurs

Toutes les erreurs retournent un JSON avec ce format :

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Les données fournies sont invalides",
    "details": {
      "amount": ["Ce champ est requis"],
      "account_id": ["Compte invalide ou inexistant"]
    }
  }
}
```

---

### Codes d'erreur personnalisés

| Code                    | Description                                        |
|-------------------------|----------------------------------------------------|
| VALIDATION_ERROR        | Erreur de validation des données                   |
| AUTHENTICATION_FAILED   | Échec de l'authentification                        |
| TOKEN_EXPIRED           | Token JWT expiré                                   |
| INSUFFICIENT_BALANCE    | Solde insuffisant                                  |
| RESOURCE_NOT_FOUND      | Ressource demandée non trouvée                     |
| PERMISSION_DENIED       | Permissions insuffisantes                          |
| DUPLICATE_ENTRY         | Tentative de création d'un doublon                 |
| WEBAUTHN_ERROR          | Erreur lors de l'authentification WebAuthn         |

---

## En-têtes requis

### Pour toutes les requêtes authentifiées

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Pour les requêtes avec token API

```
Authorization: ApiToken <api_token>
Content-Type: application/json
```

---

## Exemples d'utilisation

### cURL

```bash
# Créer une transaction
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "category_id": 3,
    "amount": -45.80,
    "description": "Courses",
    "transaction_date": "2026-02-03"
  }'
```

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
headers = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGc...",
    "Content-Type": "application/json"
}

# Créer une transaction
response = requests.post(
    f"{BASE_URL}/transactions",
    headers=headers,
    json={
        "account_id": 1,
        "category_id": 3,
        "amount": -45.80,
        "description": "Courses",
        "transaction_date": "2026-02-03"
    }
)

print(response.json())
```

### JavaScript (fetch)

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';
const token = 'eyJ0eXAiOiJKV1QiLCJhbGc...';

// Créer une transaction
async function createTransaction() {
  const response = await fetch(`${BASE_URL}/transactions`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      account_id: 1,
      category_id: 3,
      amount: -45.80,
      description: 'Courses',
      transaction_date: '2026-02-03'
    })
  });
  
  const data = await response.json();
  console.log(data);
}
```

---

## Rate Limiting

L'API applique des limites de taux pour prévenir les abus :

- **Avec JWT :** 1000 requêtes par heure
- **Avec API Token :** 500 requêtes par heure
- **Endpoints d'authentification :** 10 tentatives par heure

Les en-têtes de réponse incluent :

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 998
X-RateLimit-Reset: 1675430400
```

---

## Versioning

L'API utilise le versioning par URL : `/api/v1/`

Les versions obsolètes seront maintenues pendant au moins 6 mois après l'introduction d'une nouvelle version majeure.

---

## À compléter

- [ ] Endpoints pour export de données (CSV, PDF)
- [ ] Webhooks pour notifications
- [ ] Endpoints pour pièces jointes (reçus)
- [ ] Documentation OpenAPI/Swagger
