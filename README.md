# Budget Tracker - Application de Suivi de Budget

Application web complète pour la gestion et le suivi détaillé de budgets personnels avec support multi-comptes, analyse graphique et authentification sécurisée par passkeys.

---

## 🚀 Fonctionnalités principales

- 💰 **Gestion de budgets** avec objectifs et calcul automatique des montants mensuels
- 💳 **Multi-comptes** (courant, épargne, etc.)
- 📊 **Transactions** manuelles et récurrentes
- 🏷️ **Catégories** personnalisables
- 📈 **Graphiques** de suivi et d'analyse (D3.js)
- 🔐 **Authentification WebAuthn** (passkeys) sans mot de passe
- 📱 **API REST** pour intégration mobile
- 🔍 **Recherche avancée** dans les transactions

---

## 🛠️ Technologies

### Frontend
- **Nuxt.js 3** - Framework Vue.js avec SSR
- **Nuxt UI** - Composants UI
- **D3.js** - Visualisations de données
- **WebAuthn** - Authentification par passkeys

### Backend
- **Django 5.x** - Framework Python
- **Django REST Framework** - API REST
- **PostgreSQL 16** - Base de données
- **JWT** - Gestion des sessions

### Infrastructure
- **Docker & Docker Compose** - Containerisation
- **Nginx** - Reverse proxy
- **Gunicorn** - Serveur WSGI

---

## 📋 Prérequis

### Pour le développement
- **Node.js** 20+
- **Python** 3.11+
- **PostgreSQL** 16+
- **Git**

### Pour le déploiement (Raspberry Pi)
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Raspberry Pi 4** (4GB RAM recommandé)

---

## 🚀 Installation rapide

### Option 1 : Développement local

#### Backend
```bash
# Cloner le projet
git clone https://github.com/votre-utilisateur/budget-tracker.git
cd budget-tracker/backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

#### Frontend
```bash
cd ../frontend

# Installer les dépendances
npm install

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# Lancer le serveur de développement
npm run dev
```

L'application sera accessible sur :
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000/api/v1
- Admin Django : http://localhost:8000/admin

---

### Option 2 : Docker (Production)

```bash
# Cloner le projet
git clone https://github.com/votre-utilisateur/budget-tracker.git
cd budget-tracker

# Configurer les variables d'environnement
cp .env.example .env
# ⚠️ IMPORTANT : Modifier .env avec des valeurs sécurisées

# Construire et lancer
docker-compose up -d

# Appliquer les migrations
docker-compose exec backend python manage.py migrate

# Créer un superutilisateur
docker-compose exec backend python manage.py createsuperuser
```

L'application sera accessible sur :
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000/api/v1

---

## 📚 Documentation

La documentation complète du projet est disponible dans les fichiers suivants :

- **[PROJET_SUIVI_BUDGET.md](./PROJET_SUIVI_BUDGET.md)** - Vue d'ensemble et objectifs du projet
- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Architecture technique détaillée
- **[DATABASE.md](./docs/DATABASE.md)** - Schéma de base de données et requêtes
- **[API.md](./docs/API.md)** - Documentation complète de l'API REST
- **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** - Guide de déploiement sur Raspberry Pi

---

## 🏗️ Structure du projet

```
budget-tracker/
├── frontend/                 # Application Nuxt.js
│   ├── components/          # Composants Vue réutilisables
│   ├── pages/               # Pages de l'application
│   ├── composables/         # Logique réutilisable
│   ├── assets/              # Ressources statiques
│   ├── nuxt.config.ts       # Configuration Nuxt
│   ├── package.json
│   └── Dockerfile
│
├── backend/                  # Application Django
│   ├── api/                 # Configuration DRF
│   ├── accounts/            # App gestion des comptes
│   ├── transactions/        # App transactions
│   ├── budgets/             # App budgets
│   ├── categories/          # App catégories
│   ├── authentication/      # WebAuthn + JWT
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── nginx/                    # Configuration Nginx
│   └── nginx.conf
│
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md
│   ├── DATABASE.md
│   ├── API.md
│   └── DEPLOYMENT.md
│
├── scripts/                  # Scripts utilitaires
│   └── backup.sh
│
├── docker-compose.yml        # Orchestration Docker
├── .env.example              # Template variables d'environnement
├── .gitignore
├── PROJET_SUIVI_BUDGET.md
└── README.md
```

---

## 🔒 Sécurité

### Authentification
- **WebAuthn/FIDO2** pour authentification sans mot de passe
- Support des gestionnaires de passkeys (Proton Pass, 1Password, etc.)
- **JWT** pour la gestion des sessions
- Tokens API révocables pour l'accès mobile

### Bonnes pratiques
- ✅ Toutes les communications en HTTPS (production)
- ✅ Protection CSRF activée
- ✅ Rate limiting sur l'API
- ✅ Validation des entrées côté backend
- ✅ Row Level Security sur PostgreSQL
- ✅ Cookies httpOnly pour les tokens

⚠️ **Important** : 
- Ne jamais commiter le fichier `.env`
- Changer toutes les clés secrètes par défaut
- Utiliser des mots de passe forts pour la base de données
- Activer HTTPS en production

---

## 🧪 Tests

### Backend
```bash
cd backend

# Lancer tous les tests
python manage.py test

# Lancer les tests avec coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend
```bash
cd frontend

# Lancer les tests unitaires
npm run test

# Lancer les tests e2e
npm run test:e2e
```

---

## 📱 API Mobile

L'application expose une API REST complète pour permettre l'intégration avec des applications mobiles.

### Génération d'un token API

1. Se connecter à l'application web
2. Aller dans **Paramètres** → **Tokens API**
3. Cliquer sur **Créer un token**
4. Donner un nom au token (ex: "Mon iPhone")
5. Copier le token généré

### Utilisation

```bash
# Exemple : Créer une transaction
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: ApiToken votre-token-ici" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "category_id": 3,
    "amount": -45.80,
    "description": "Courses",
    "transaction_date": "2026-02-03"
  }'
```

Voir **[API.md](./docs/API.md)** pour la documentation complète.

---

## 🔧 Configuration

### Variables d'environnement essentielles

#### Backend (.env)
```bash
# Django
SECRET_KEY=<générer-une-clé-sécurisée>
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/budget_db

# JWT
JWT_ACCESS_TOKEN_LIFETIME=15  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # jours
```

#### Frontend (.env)
```bash
# API
NUXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
```

---

## 📊 Utilisation

### Créer un budget

1. Se connecter à l'application
2. Aller dans **Budgets** → **Nouveau budget**
3. Remplir les informations :
   - Nom (ex: "Matériel sono")
   - Montant cible (ex: 500€)
   - Date limite (ex: 30/06/2026)
   - Catégorie (optionnel)
4. Le montant mensuel est calculé automatiquement

### Ajouter une transaction

1. Aller dans **Transactions** → **Nouvelle transaction**
2. Sélectionner le compte
3. Choisir la catégorie
4. Entrer le montant (négatif pour une dépense)
5. Ajouter une description
6. Sélectionner la date

### Configurer une transaction récurrente

1. Lors de la création d'une transaction, cocher "Récurrent"
2. Définir la fréquence (quotidien, hebdomadaire, mensuel, annuel)
3. Définir l'intervalle (ex: tous les 2 mois)
4. Définir la date de début
5. Optionnel : définir une date de fin

---

## 🤝 Contribution

Les contributions sont les bienvenues ! 

### Workflow recommandé

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commiter vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Pousser vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Standards de code

- **Python** : PEP 8
- **JavaScript** : ESLint avec config standard
- **Commits** : Messages en français, descriptifs
- **Tests** : Écrire des tests pour les nouvelles fonctionnalités

---

## 🐛 Signaler un bug

Si vous trouvez un bug, veuillez ouvrir une issue avec :
- Description claire du problème
- Étapes pour reproduire
- Comportement attendu vs comportement actuel
- Logs si disponibles
- Version de l'application

---

## 📝 Roadmap

### Version 1.0 (MVP) - En cours
- [x] Authentification WebAuthn
- [x] Gestion des comptes
- [x] Gestion des transactions
- [x] Gestion des budgets
- [x] Catégories personnalisables
- [x] Graphiques de base
- [x] API REST
- [ ] Tests unitaires complets
- [ ] Documentation utilisateur

### Version 2.0 - À venir
- [ ] Import automatique depuis banques (API bancaires)
- [ ] Export de données (CSV, PDF, Excel)
- [ ] Application mobile native
- [ ] Notifications push
- [ ] Partage de budgets entre utilisateurs
- [ ] Cache Redis pour performances
- [ ] WebSocket pour mises à jour temps réel

### Version 3.0 - Futur
- [ ] Intelligence artificielle pour prédictions
- [ ] Recommandations personnalisées
- [ ] Intégration avec d'autres services financiers
- [ ] Mode multi-devises avancé

---

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👨‍💻 Auteur

Votre Nom - [@votre-handle](https://twitter.com/votre-handle)

---

## 🙏 Remerciements

- [Nuxt.js](https://nuxt.com/) pour le framework frontend
- [Django](https://www.djangoproject.com/) pour le framework backend
- [WebAuthn](https://webauthn.io/) pour l'authentification sécurisée
- [D3.js](https://d3js.org/) pour les visualisations
- La communauté open-source

---

## 💬 Support

- 📧 Email : votre-email@example.com
- 💬 Discord : [Lien vers serveur Discord]
- 🐛 Issues : [GitHub Issues](https://github.com/votre-utilisateur/budget-tracker/issues)

---

## ⚡ Quick Start TL;DR

```bash
# Clone
git clone https://github.com/votre-utilisateur/budget-tracker.git
cd budget-tracker

# Configure
cp .env.example .env
# ⚠️ Modifier .env avec vos valeurs

# Docker
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Ready!
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/api/v1
```

---

**Happy budgeting! 💰📊**
