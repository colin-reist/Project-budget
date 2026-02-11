# 🐳 Déploiement avec Docker

Ce guide explique comment déployer l'application Budget Tracker avec Docker et garantir la persistance des données lors des mises à jour.

## 📋 Prérequis

- **Docker** (v20.10+): https://docs.docker.com/get-docker/
- **Docker Compose** (v2.0+): Inclus avec Docker Desktop

## 🚀 Démarrage Rapide

### 1. Préparation de l'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Générer une clé secrète Django
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Éditer .env et ajouter la clé générée
```

### 2. Lancer l'application

```bash
# Démarrer les conteneurs
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

L'application sera disponible à:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Base de données**: localhost:5432

## 💾 Persistance des Données

### Architecture des Volumes

L'application utilise 3 volumes Docker pour persister les données:

```
postgres_data/      → Données PostgreSQL (base de données complète)
static_volume/      → Fichiers statiques Django
media_volume/       → Fichiers média utilisateurs
```

**CRUCIAL**: Ces volumes persisten automatiquement même après:
- ✅ Arrêt des conteneurs
- ✅ Mise à jour du code
- ✅ Recréation des conteneurs
- ❌ Suppression AVEC `-v` flag (destruction intentionnelle)

## 🔄 Mises à Jour SANS Perte de Données

### Frontend (HTML/CSS/JS)

```bash
git pull origin main
docker-compose build frontend
docker-compose up -d frontend
```

**Impact**:
- ✅ Code mis à jour
- ✅ Données utilisateur: CONSERVÉES
- ✅ Base de données: INTACTE

### Backend (Django)

```bash
git pull origin main
docker-compose build backend
docker-compose up -d backend
```

**Impact**:
- ✅ Code mis à jour
- ✅ Migrations appliquées automatiquement
- ✅ Données utilisateur: CONSERVÉES

### Tout (Frontend + Backend)

```bash
git pull origin main
docker-compose build
docker-compose up -d
```

## 🗄️ Gestion de la Base de Données

### Sauvegarde

```bash
# Créer une sauvegarde SQL
docker-compose exec database pg_dump -U budget_user budget_db > backup.sql

# Sauvegarde datée
docker-compose exec database pg_dump -U budget_user budget_db > backups/backup-$(date +%Y%m%d).sql
```

### Restauration

```bash
# Restaurer une sauvegarde
docker-compose exec -T database psql -U budget_user budget_db < backup.sql
```

## 🛑 Arrêt et Nettoyage

### Arrêter (données sauvegardées)
```bash
docker-compose down
# Les volumes persisten automatiquement!
```

### Supprimer TOUT (⚠️ PERTE DE DONNÉES)
```bash
docker-compose down -v
# Cela supprime aussi les volumes!
```

## 📊 Commandes Utiles

### Logs
```bash
docker-compose logs -f backend      # Logs du backend
docker-compose logs -f frontend     # Logs du frontend
docker-compose logs -f database     # Logs de la BD
```

### Accès à la base de données
```bash
docker-compose exec database psql -U budget_user -d budget_db
```

### Vérifier l'état
```bash
docker-compose ps
docker volume ls
docker system df
```

## 🔐 Configuration Sécurité

Éditer `.env`:

```bash
# Générer une clé sécurisée
SECRET_KEY=<clé-générée>

# Mot de passe base de données
POSTGRES_PASSWORD=<mot-de-passe-fort>

# Production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

## 📝 Résumé des Données

| Élément | Localisation | Persiste? |
|---------|--------------|-----------|
| Utilisateurs | postgres_data | ✅ Oui |
| Transactions | postgres_data | ✅ Oui |
| Comptes | postgres_data | ✅ Oui |
| Budgets | postgres_data | ✅ Oui |
| Fichiers statiques | static_volume | ✅ Oui |
| Uploads média | media_volume | ✅ Oui |

## 🎯 Checkliste

- [x] Dockerfiles configurés (multi-stage)
- [x] Docker-compose avec PostgreSQL
- [x] Volumes pour persistance
- [x] Health checks
- [x] Variables d'environnement
- [x] .dockerignore
- [x] Migrations automatiques
- [x] Utilisateurs non-root
- [x] Réseaux personnalisés

**Vous êtes prêt pour la production!** 🚀
