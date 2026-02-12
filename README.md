# Budget Tracker

Application web complète pour la gestion et le suivi détaillé de budgets personnels avec support multi-comptes, analyse graphique et authentification sécurisée par passkeys.

---

## ✨ Fonctionnalités

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

| Frontend | Backend | Infrastructure |
|----------|---------|----------------|
| Nuxt.js 3 | Django 5.x | Docker |
| Nuxt UI | Django REST Framework | PostgreSQL 16 |
| D3.js | JWT + WebAuthn | Nginx/Caddy |

---

## 🚀 Installation Rapide

### Option 1 : Docker (Recommandé)

```bash
# Cloner et configurer
git clone https://github.com/votre-utilisateur/budget-tracker.git
cd budget-tracker
cp .env.example .env

# ⚠️ IMPORTANT : Éditer .env et changer SECRET_KEY et POSTGRES_PASSWORD

# Lancer
docker-compose up -d

# Initialiser
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

**Accès :**
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000/api/v1
- Admin : http://localhost:8000/admin

📚 **Documentation complète** : [docs/DOCKER.md](docs/DOCKER.md)

---

### Option 2 : Raspberry Pi (Auto-hébergement)

```bash
# SSH sur le Raspberry Pi
ssh pi@raspberrypi.local

# Installation automatisée
git clone https://github.com/votre-utilisateur/budget-tracker.git
cd budget-tracker
sudo bash scripts/install-rpi.sh
```

📚 **Documentation complète** : [docs/RASPBERRY_PI.md](docs/RASPBERRY_PI.md)

---

### Option 3 : Développement Local

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[docs/README.md](docs/README.md)** | Index de la documentation |
| **[docs/DOCKER.md](docs/DOCKER.md)** | Guide Docker complet |
| **[docs/RASPBERRY_PI.md](docs/RASPBERRY_PI.md)** | Déploiement Raspberry Pi |
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | Architecture technique |
| **[docs/DATABASE.md](docs/DATABASE.md)** | Schéma de base de données |
| **[docs/API.md](docs/API.md)** | Documentation API REST |
| **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** | Guide de déploiement |

---

## 🏗️ Structure du Projet

```
budget-tracker/
├── backend/                 # Django REST API
│   ├── accounts/           # Gestion des comptes bancaires
│   ├── authentication/     # WebAuthn + JWT
│   ├── budgets/            # Gestion des budgets
│   ├── categories/         # Catégories personnalisables
│   ├── transactions/       # Transactions et récurrences
│   └── config/             # Configuration Django
│
├── frontend/                # Application Nuxt.js
│   ├── components/         # Composants Vue réutilisables
│   ├── pages/              # Pages de l'application
│   ├── composables/        # Logique réutilisable
│   └── layouts/            # Layouts
│
├── docs/                    # Documentation complète
├── scripts/                 # Scripts utilitaires
├── nginx/                   # Configuration Nginx
├── docker-compose.yml       # Production
├── docker-compose.dev.yml   # Développement
└── .env.example             # Template de configuration
```

---

## 🔒 Sécurité

- ✅ **WebAuthn/FIDO2** : Authentification sans mot de passe
- ✅ **JWT** : Gestion sécurisée des sessions
- ✅ **HTTPS** : Obligatoire en production
- ✅ **CORS** : Protection contre les requêtes non autorisées
- ✅ **Rate Limiting** : Protection contre les abus
- ✅ **Row Level Security** : Isolation des données utilisateurs

⚠️ **Avant de déployer :**
- Changer `SECRET_KEY` dans `.env`
- Changer `POSTGRES_PASSWORD` dans `.env`
- Utiliser `DEBUG=False` en production
- Activer HTTPS (Caddy/Nginx)

---

## 📱 API Mobile

L'application expose une API REST complète pour permettre l'intégration mobile.

**Exemple d'utilisation :**

```bash
# Générer un token API dans l'interface web
# Paramètres → Tokens API → Créer un token

# Utiliser le token
curl -X POST https://yourdomain.com/api/v1/transactions \
  -H "Authorization: ApiToken votre-token-ici" \
  -H "Content-Type: application/json" \
  -d '{"account_id": 1, "amount": -45.80, "description": "Courses"}'
```

📚 **Documentation API complète** : [docs/API.md](docs/API.md)

---

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

**Standards :**
- Python : PEP 8
- JavaScript : ESLint
- Commits : Messages descriptifs en français
- Tests : Requis pour les nouvelles fonctionnalités

---

## 🐛 Support

- 📧 Email : votre-email@example.com
- 🐛 Issues : [GitHub Issues](https://github.com/votre-utilisateur/budget-tracker/issues)
- 💬 Discussions : [GitHub Discussions](https://github.com/votre-utilisateur/budget-tracker/discussions)

---

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## ⚡ Quick Start TL;DR

```bash
# Clone
git clone https://github.com/votre-utilisateur/budget-tracker.git
cd budget-tracker

# Configure
cp .env.example .env
# ⚠️ Éditer .env et changer SECRET_KEY + POSTGRES_PASSWORD

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

Pour plus d'informations, consultez la [documentation complète](docs/README.md).
