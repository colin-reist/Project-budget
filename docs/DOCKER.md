# 🐳 Guide Docker - Budget Tracker

Ce guide explique comment déployer et gérer l'application Budget Tracker avec Docker.

---

## 📋 Prérequis

- **Docker** (v20.10+): https://docs.docker.com/get-docker/
- **Docker Compose** (v2.0+): Inclus avec Docker Desktop

---

## ⚡ Quick Start

### Installation Initiale (Une fois)

```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/Project-budget.git
cd Project-budget

# 2. Créer la configuration
cp .env.example .env

# 3. Générer une clé secrète Django
python -c "import secrets; print(secrets.token_urlsafe(50))"
# Copier la clé générée dans .env → SECRET_KEY

# 4. Éditer .env avec vos valeurs
nano .env

# 5. Lancer l'application
docker-compose up -d

# 6. Appliquer les migrations
docker-compose exec backend python manage.py migrate

# 7. Créer un superutilisateur
docker-compose exec backend python manage.py createsuperuser
```

✅ **Application ready!**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1
- Admin Django: http://localhost:8000/admin

---

## 🔄 Mise à Jour (Sans Perte de Données)

### Méthode Rapide (Scripts automatisés)

#### Windows
```bash
deploy.bat
# Choisir l'option 1 pour déploiement complet
```

#### Linux/Mac
```bash
./deploy.sh deploy
# ou: ./deploy.sh deploy-frontend
# ou: ./deploy.sh deploy-backend
```

### Méthode Manuelle

#### Mise à jour du Frontend uniquement
```bash
git pull origin main
docker-compose build frontend
docker-compose up -d frontend
```

**Impact:**
- ✅ Code mis à jour
- ✅ Données utilisateur: CONSERVÉES
- ✅ Base de données: INTACTE

#### Mise à jour du Backend uniquement
```bash
git pull origin main
docker-compose build backend
docker-compose up -d backend
```

**Impact:**
- ✅ Code mis à jour
- ✅ Migrations appliquées automatiquement
- ✅ Données utilisateur: CONSERVÉES

#### Mise à jour complète (Frontend + Backend)
```bash
git pull origin main
docker-compose build
docker-compose up -d
```

---

## 💾 Persistance des Données

### Architecture des Volumes

L'application utilise 3 volumes Docker pour persister les données:

```
postgres_data/      → Données PostgreSQL (base de données complète)
static_volume/      → Fichiers statiques Django
media_volume/       → Fichiers média utilisateurs
```

**CRUCIAL**: Ces volumes persistent automatiquement même après:
- ✅ Arrêt des conteneurs (`docker-compose down`)
- ✅ Mise à jour du code
- ✅ Recréation des conteneurs
- ❌ Suppression AVEC `-v` flag (destruction intentionnelle)

### Tableau de Persistance

| Élément | Localisation | Persiste? |
|---------|--------------|-----------|
| Utilisateurs | postgres_data | ✅ Oui |
| Transactions | postgres_data | ✅ Oui |
| Comptes | postgres_data | ✅ Oui |
| Budgets | postgres_data | ✅ Oui |
| Fichiers statiques | static_volume | ✅ Oui |
| Uploads média | media_volume | ✅ Oui |

---

## 🗄️ Gestion de la Base de Données

### Sauvegarde

```bash
# Créer une sauvegarde SQL
docker-compose exec database pg_dump -U budget_user budget_db > backup.sql

# Sauvegarde datée (recommandé)
docker-compose exec database pg_dump -U budget_user budget_db > backups/backup-$(date +%Y%m%d-%H%M%S).sql

# Utiliser le script automatisé
./scripts/backup.sh
```

### Restauration

```bash
# Restaurer une sauvegarde
docker-compose exec -T database psql -U budget_user budget_db < backup.sql

# Ou depuis le dossier backups
docker-compose exec -T database psql -U budget_user budget_db < backups/backup-20260212-143000.sql
```

### Accès direct à la base de données

```bash
# Via psql
docker-compose exec database psql -U budget_user -d budget_db

# Exemples de commandes SQL
\dt              # Lister les tables
\d+ accounts_account  # Détails d'une table
SELECT * FROM accounts_account;
\q               # Quitter
```

---

## 📊 Commandes Utiles

### Gestion des conteneurs

```bash
# Démarrer l'application
docker-compose up -d

# Arrêter l'application (données conservées)
docker-compose down

# Redémarrer un service spécifique
docker-compose restart backend
docker-compose restart frontend
docker-compose restart database

# Voir l'état des conteneurs
docker-compose ps

# Voir les ressources utilisées
docker stats
```

### Logs et debugging

```bash
# Logs de tous les services
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database

# Logs des 100 dernières lignes
docker-compose logs --tail=100 backend

# Logs depuis 10 minutes
docker-compose logs --since 10m backend
```

### Exécution de commandes dans les conteneurs

```bash
# Django management commands
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic
docker-compose exec backend python manage.py shell

# Shell bash dans un conteneur
docker-compose exec backend bash
docker-compose exec frontend sh

# Vérifier les variables d'environnement
docker-compose exec backend env
```

### Gestion des volumes

```bash
# Lister les volumes
docker volume ls

# Inspecter un volume
docker volume inspect budget-tracker_postgres_data

# Voir l'espace disque utilisé
docker system df
```

---

## 🛑 Arrêt et Nettoyage

### Arrêter (données sauvegardées)
```bash
docker-compose down
# Les volumes persistent automatiquement!
```

### Supprimer TOUT (⚠️ PERTE DE DONNÉES)
```bash
# ATTENTION: Cela supprime TOUS les volumes et TOUTES les données!
docker-compose down -v

# Pour supprimer aussi les images
docker-compose down -v --rmi all
```

### Nettoyage des ressources inutilisées
```bash
# Nettoyer les images non utilisées
docker image prune -a

# Nettoyer les volumes non utilisés
docker volume prune

# Nettoyage complet du système Docker
docker system prune -a --volumes
```

---

## 🔐 Configuration Sécurité

### Variables d'environnement essentielles

Éditer `.env`:

```bash
# Générer une clé sécurisée
SECRET_KEY=<clé-générée-avec-secrets.token_urlsafe>

# Mot de passe base de données
POSTGRES_PASSWORD=<mot-de-passe-fort-unique>

# Production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# WebAuthn (si domaine personnalisé)
WEBAUTHN_RP_ID=yourdomain.com
WEBAUTHN_ORIGIN=https://yourdomain.com

# API Frontend
NUXT_PUBLIC_API_BASE=https://yourdomain.com/api/v1
```

### Checklist de sécurité

- [ ] `SECRET_KEY` changée et sécurisée
- [ ] `POSTGRES_PASSWORD` fort et unique
- [ ] `DEBUG=False` en production
- [ ] `ALLOWED_HOSTS` configuré correctement
- [ ] HTTPS activé en production (via Caddy/Nginx)
- [ ] Certificats SSL valides
- [ ] Backups automatiques configurés
- [ ] Fichiers `.env` dans `.gitignore`

---

## 🚀 Développement vs Production

### Mode Développement

Utiliser `docker-compose.dev.yml`:

```bash
# Lancer en mode développement
docker-compose -f docker-compose.dev.yml up -d

# Avec hot-reload activé
docker-compose -f docker-compose.dev.yml up

# Variables pour dev
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Mode Production

Utiliser `docker-compose.yml`:

```bash
# Lancer en production
docker-compose up -d

# Variables pour production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

---

## 🎯 Checkliste de Déploiement

- [x] Dockerfiles configurés (multi-stage)
- [x] Docker-compose avec PostgreSQL
- [x] Volumes pour persistance
- [x] Health checks
- [x] Variables d'environnement
- [x] .dockerignore
- [x] Migrations automatiques
- [x] Utilisateurs non-root
- [x] Réseaux personnalisés

---

## 🐛 Troubleshooting

### Le conteneur backend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs backend

# Problèmes courants:
# - SECRET_KEY manquante → Vérifier .env
# - Base de données non accessible → Vérifier que le service database est up
# - Erreur de migration → docker-compose exec backend python manage.py migrate
```

### Le frontend ne se connecte pas au backend

```bash
# Vérifier la variable NUXT_PUBLIC_API_BASE dans .env
# Doit pointer vers: http://localhost:8000/api/v1 (dev) ou https://yourdomain.com/api/v1 (prod)

# Vérifier les CORS dans le backend (.env)
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### La base de données est vide après redémarrage

```bash
# Vérifier que les volumes existent
docker volume ls | grep postgres_data

# Si le volume n'existe pas, il a été supprimé
# Restaurer depuis une sauvegarde:
docker-compose exec -T database psql -U budget_user budget_db < backups/backup-latest.sql
```

### Espace disque saturé

```bash
# Vérifier l'espace utilisé
docker system df

# Nettoyer les ressources inutilisées
docker system prune -a

# Supprimer les logs volumineux
docker-compose logs --tail=0 backend > /dev/null
```

---

## 📚 Résumé des Commandes

| Situation | Commande | Données |
|-----------|----------|---------|
| Premier démarrage | `docker-compose up -d` | Safe |
| Update frontend | `docker-compose build frontend && docker-compose up -d frontend` | ✅ Preserved |
| Update backend | `docker-compose build backend && docker-compose up -d backend` | ✅ Preserved |
| Update complet | `docker-compose build && docker-compose up -d` | ✅ Preserved |
| Arrêter | `docker-compose down` | ✅ Preserved |
| Reset complet ⚠️ | `docker-compose down -v` | ❌ DELETED |
| Backup BD | `docker-compose exec database pg_dump ...` | Safe |
| Logs | `docker-compose logs -f backend` | Read-only |

---

**👉 Les données persistent tant que vous n'ajoutez pas `-v` à `docker-compose down`!**

**Vous êtes prêt pour la production! 🚀**
