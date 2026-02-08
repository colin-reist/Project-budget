# Frontend - Nuxt.js

Application frontend du Budget Tracker construite avec Nuxt.js 3, Nuxt UI et TypeScript.

## 🎯 Structure du projet

```
frontend/
├── app.vue              # Point d'entrée de l'application
├── nuxt.config.ts       # Configuration Nuxt
├── package.json         # Dépendances
├── types/               # Types TypeScript
│   └── index.ts         # Types principaux (User, Account, Transaction, etc.)
├── composables/         # Logique réutilisable
│   ├── useApi.ts        # Client API avec authentification
│   ├── useAuth.ts       # Gestion de l'authentification
│   └── useWebAuthn.ts   # Authentification WebAuthn/Passkeys
├── middleware/          # Middlewares de navigation
│   ├── auth.ts          # Protection des routes authentifiées
│   └── guest.ts         # Redirection pour utilisateurs connectés
├── layouts/             # Layouts de l'application
│   ├── default.vue      # Layout principal avec navigation
│   └── auth.vue         # Layout pour pages d'authentification
├── pages/               # Pages de l'application (routing automatique)
│   ├── index.vue        # Dashboard principal
│   ├── login.vue        # Page de connexion
│   ├── accounts/
│   │   └── index.vue    # Liste des comptes
│   ├── transactions/
│   │   └── index.vue    # Liste des transactions
│   └── budgets/
│       └── index.vue    # Gestion des budgets
├── components/          # Composants Vue (à développer)
├── assets/              # Assets statiques
├── Dockerfile           # Configuration Docker
└── .dockerignore        # Exclusions Docker
```

## ✅ Fonctionnalités implémentées

### Authentification
- ✅ Composable `useAuth` pour la gestion de sessions
- ✅ Composable `useWebAuthn` pour l'authentification par Passkeys
- ✅ Middlewares de protection des routes
- ✅ Gestion des tokens JWT (access + refresh)

### Pages
- ✅ Dashboard avec vue d'ensemble des finances
- ✅ Page de connexion (mot de passe + WebAuthn)
- ✅ Page de gestion des comptes bancaires
- ✅ Page de gestion des transactions
- ✅ Page de gestion des budgets

### Infrastructure
- ✅ Configuration Nuxt UI
- ✅ Types TypeScript complets
- ✅ Client API centralisé
- ✅ Layouts responsive

## 🚀 Installation et démarrage

### Prérequis
- Node.js 20+
- npm ou pnpm

### Installation des dépendances
```bash
npm install
```

### Configuration
Créez un fichier `.env` à partir de `.env.example`:
```bash
cp .env.example .env
```

Modifiez l'URL de l'API si nécessaire:
```env
NUXT_PUBLIC_API_BASE=http://localhost:8000
```

### Développement
```bash
npm run dev
```

L'application sera disponible sur http://localhost:3000

### Build de production
```bash
npm run build
```

### Prévisualisation de production
```bash
npm run preview
```

## 🔧 Technologies utilisées

- **Nuxt 3** - Framework Vue.js avec SSR
- **Nuxt UI** - Bibliothèque de composants UI
- **TypeScript** - Typage statique
- **@simplewebauthn/browser** - Authentification WebAuthn
- **D3.js** - Visualisation de données (à intégrer)

## 📋 Prochaines étapes

### Composants à créer
- [ ] Composants de formulaires réutilisables
  - [ ] `AccountForm.vue` - Création/édition de comptes
  - [ ] `TransactionForm.vue` - Création/édition de transactions
  - [ ] `BudgetForm.vue` - Création/édition de budgets
- [ ] Composants de graphiques D3.js
  - [ ] `ExpensesPieChart.vue` - Graphique circulaire des dépenses
  - [ ] `BalanceLineChart.vue` - Évolution du solde
  - [ ] `BudgetProgressChart.vue` - Progression des budgets
- [ ] Composants UI
  - [ ] `ConfirmDialog.vue` - Dialogue de confirmation
  - [ ] `LoadingSpinner.vue` - Indicateur de chargement
  - [ ] `EmptyState.vue` - État vide générique

### Fonctionnalités à développer
- [ ] Intégration complète des graphiques D3.js
- [ ] Gestion des catégories personnalisées
- [ ] Système de filtres avancés
- [ ] Export de données (CSV, PDF)
- [ ] Mode hors ligne avec cache
- [ ] Notifications en temps réel
- [ ] Support multidevise

### Améliorations UX
- [ ] Transitions et animations
- [ ] Toast notifications
- [ ] Loading states améliorés
- [ ] Error boundaries
- [ ] Skeleton loaders
- [ ] Thème sombre/clair

## 🐳 Docker

### Build de l'image
```bash
docker build -t budget-tracker-frontend .
```

### Exécution
```bash
docker run -p 3000:3000 budget-tracker-frontend
```

## 📚 Documentation API

L'application communique avec le backend Django via l'API REST. Consultez [docs/API.md](../docs/API.md) pour la documentation complète des endpoints.

## 🔐 Sécurité

- Tokens JWT stockés dans des cookies HttpOnly
- Authentification WebAuthn avec Passkeys
- Protection CSRF
- Validation côté client et serveur
- HTTPS obligatoire en production
