# Architecture Technique - Application de Suivi de Budget

## Vue d'ensemble

Application web full-stack avec architecture séparée, déployée via Docker pour faciliter l'installation sur Raspberry Pi.

---

## Schéma d'architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Navigateur Web                          │
│                    (Interface utilisateur)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND - Nuxt.js                         │
│                         Port: 3000                              │
│                                                                 │
│  - Nuxt UI (composants)                                         │
│  - WebAuthn (passkeys)                                          │
│  - D3.js (graphiques)                                           │
│  - Composables Vue                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ API REST (JSON)
                             │ JWT Token
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND - Django API                         │
│                         Port: 8000                              │
│                                                                 │
│  - Django REST Framework                                        │
│  - WebAuthn validation                                          │
│  - JWT authentication                                           │
│  - Business logic                                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ SQL
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BASE DE DONNÉES - PostgreSQL                  │
│                         Port: 5432                              │
│                                                                 │
│  - Comptes bancaires                                            │
│  - Transactions                                                 │
│  - Budgets                                                      │
│  - Utilisateurs & authentification                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Composants

### 1. Frontend - Nuxt.js (Port 3000)

**Responsabilités :**
- Interface utilisateur responsive
- Gestion de l'état de l'application
- Visualisation des données (graphiques D3.js)
- Authentification WebAuthn côté client
- Communication avec l'API backend

**Technologies :**
- Nuxt.js 3
- Nuxt UI
- Composables Vue (gestion d'état)
- D3.js (visualisations)
- @simplewebauthn/browser

**Container Docker :** `frontend`

---

### 2. Backend - Django API (Port 8000)

**Responsabilités :**
- API RESTful pour toutes les opérations
- Logique métier (calculs de budgets, récurrence, etc.)
- Validation et sécurité
- Authentification WebAuthn et JWT
- Gestion des utilisateurs

**Technologies :**
- Python 3.11+
- Django 5.x
- Django REST Framework
- djangorestframework-simplejwt
- py_webauthn (validation passkeys)

**Container Docker :** `backend`

---

### 3. Base de données - PostgreSQL (Port 5432)

**Responsabilités :**
- Stockage persistant des données
- Relations et intégrité des données
- Transactions ACID

**Technologies :**
- PostgreSQL 16

**Container Docker :** `database`

---

## Flow d'authentification

### Connexion via Passkey (WebAuthn)

```
1. Utilisateur → Frontend : Clique sur "Se connecter"
2. Frontend → Backend : Demande un challenge WebAuthn
3. Backend → Frontend : Retourne challenge + options
4. Frontend : Déclenche WebAuthn (Proton Pass)
5. Utilisateur : Valide avec Proton Pass
6. Frontend → Backend : Envoie la réponse signée
7. Backend : Valide la signature
8. Backend → Frontend : Retourne JWT token
9. Frontend : Stocke le token (cookie httpOnly)
10. Frontend : Redirige vers dashboard
```

### Requête API authentifiée

```
1. Frontend → Backend : Requête + JWT dans header Authorization
2. Backend : Valide le JWT
3. Backend : Exécute la logique métier
4. Backend : Interroge PostgreSQL si nécessaire
5. Backend → Frontend : Retourne la réponse JSON
6. Frontend : Met à jour l'interface
```

---

## Flow d'une transaction type

### Ajout d'une transaction manuelle

```
1. Utilisateur : Remplit le formulaire (montant, catégorie, compte, date)
2. Frontend : Valide les données côté client
3. Frontend → Backend : POST /api/transactions/
   {
     "amount": -50.00,
     "category_id": 3,
     "account_id": 1,
     "description": "Restaurant",
     "date": "2026-02-03"
   }
4. Backend : Valide JWT et permissions
5. Backend : Valide les données métier
6. Backend : Crée la transaction en DB
7. Backend : Met à jour le solde du compte
8. Backend : Vérifie impact sur budgets concernés
9. Backend → Frontend : Retourne transaction créée
10. Frontend : Met à jour l'interface + graphiques
```

---

## Ports utilisés

| Service    | Port interne | Port exposé (host) |
|------------|--------------|-------------------|
| Frontend   | 3000         | 3000              |
| Backend    | 8000         | 8000              |
| PostgreSQL | 5432         | 5432              |

---

## Communication entre services

### En développement
- Frontend communique avec Backend via `http://localhost:8000`
- Backend communique avec Database via `localhost:5432`

### En production (Docker)
- Frontend communique avec Backend via `http://backend:8000`
- Backend communique avec Database via `database:5432`
- Réseau Docker interne pour la sécurité

---

## Structure des répertoires

```
budget-tracker/
├── frontend/                 # Application Nuxt.js
│   ├── components/
│   ├── pages/
│   ├── composables/         # Logique réutilisable et état
│   ├── assets/
│   ├── nuxt.config.ts
│   ├── package.json
│   └── Dockerfile
│
├── backend/                  # Application Django
│   ├── api/                 # Django REST Framework
│   ├── accounts/            # App gestion comptes
│   ├── transactions/        # App transactions
│   ├── budgets/             # App budgets
│   ├── authentication/      # WebAuthn + JWT
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml       # Orchestration des services
├── .env.example             # Variables d'environnement
├── README.md
├── ARCHITECTURE.md          # Ce fichier
└── docs/
    ├── DATABASE.md
    ├── API.md
    └── DEPLOYMENT.md
```

---

## Sécurité

### Protection des données
- Toutes les communications en HTTPS (production)
- JWT stockés dans cookies httpOnly
- Validation des entrées côté backend
- Protection CSRF
- Rate limiting sur l'API

### Authentification
- WebAuthn (passkeys) pour connexion sans mot de passe
- JWT avec expiration courte (15 min)
- Refresh tokens pour sessions longues
- Tokens API révocables pour accès mobile

---

## Performance

### Frontend
- Server-Side Rendering (SSR) avec Nuxt
- Code splitting automatique
- Lazy loading des composants
- Cache des assets statiques

### Backend
- Pagination sur les listes
- Index sur les champs fréquemment recherchés
- Query optimization avec Django ORM
- Cache Redis (optionnel pour plus tard)

### Base de données
- Index sur clés étrangères
- Index sur champs de recherche (date, catégorie)
- Vacuum régulier de PostgreSQL

---

## Évolutivité future

### Phase 1 (MVP)
- Fonctionnalités de base
- Déploiement Docker simple
- PostgreSQL en container

### Phase 2
- Cache Redis
- WebSocket pour mises à jour temps réel
- Export de données (CSV, PDF)

### Phase 3
- Import automatique depuis banques (API bancaires)
- Application mobile native
- Partage de budgets entre utilisateurs

---

## Notes techniques

### Choix de PostgreSQL
- Support excellent des transactions
- Types de données avancés (JSON, dates, decimals)
- Performance pour analyses et agrégations
- Fiabilité et ACID

### Choix de Django
- ORM puissant pour requêtes complexes
- Admin panel intégré pour debug
- Écosystème mature
- Sécurité par défaut

### Choix de Nuxt.js
- SSR pour SEO et performance
- Écosystème Vue riche
- Nuxt UI pour composants cohérents
- TypeScript support

---

## À compléter

- [ ] Diagramme de déploiement détaillé
- [ ] Stratégie de backup
- [ ] Monitoring et logs
- [ ] Plan de mise à jour
