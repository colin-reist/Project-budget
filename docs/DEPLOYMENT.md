# Guide de Déploiement - Application de Suivi de Budget

## Vue d'ensemble

Ce guide explique comment déployer l'application sur un Raspberry Pi en utilisant Docker et Docker Compose.

---

## Table des matières

1. [Prérequis](#prérequis)
2. [Configuration Docker](#configuration-docker)
3. [Variables d'environnement](#variables-denvironnement)
4. [Installation sur Raspberry Pi](#installation-sur-raspberry-pi)
5. [Commandes utiles](#commandes-utiles)
6. [Backup et restauration](#backup-et-restauration)
7. [Monitoring](#monitoring)
8. [Mise à jour](#mise-à-jour)
9. [Troubleshooting](#troubleshooting)

---

## Prérequis

### Matériel requis
- **Raspberry Pi 4** (4GB RAM minimum recommandé)
- **Carte SD** (32GB minimum)
- **Alimentation** adaptée
- **Connexion Internet**

### Logiciels requis
- **Raspberry Pi OS** (64-bit recommandé)
- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)

---

## Configuration Docker

### Structure des fichiers

```
budget-tracker/
├── docker-compose.yml
├── .env
├── .env.example
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── ...
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── ...
└── nginx/
    └── nginx.conf
```

---

### docker-compose.yml

```yaml
version: '3.8'

services:
  # Base de données PostgreSQL
  database:
    image: postgres:16-alpine
    container_name: budget_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    networks:
      - budget_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend Django
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: budget_backend
    restart: unless-stopped
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}
      - CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS}
      - JWT_ACCESS_TOKEN_LIFETIME=${JWT_ACCESS_TOKEN_LIFETIME}
      - JWT_REFRESH_TOKEN_LIFETIME=${JWT_REFRESH_TOKEN_LIFETIME}
    volumes:
      - ./backend:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      database:
        condition: service_healthy
    networks:
      - budget_network
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60"

  # Frontend Nuxt.js
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - NUXT_PUBLIC_API_BASE=${NUXT_PUBLIC_API_BASE}
    container_name: budget_frontend
    restart: unless-stopped
    environment:
      - NUXT_PUBLIC_API_BASE=${NUXT_PUBLIC_API_BASE}
      - NODE_ENV=production
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.nuxt
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - budget_network
    command: node .output/server/index.mjs

  # Nginx (reverse proxy - optionnel)
  nginx:
    image: nginx:alpine
    container_name: budget_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    depends_on:
      - frontend
      - backend
    networks:
      - budget_network

volumes:
  postgres_data:
    driver: local
  static_volume:
    driver: local
  media_volume:
    driver: local

networks:
  budget_network:
    driver: bridge
```

---

### backend/Dockerfile

```dockerfile
# Stage 1: Base
FROM python:3.11-slim as base

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies
FROM base as dependencies

# Copier requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 3: Production
FROM dependencies as production

# Copier le code de l'application
COPY . .

# Créer un utilisateur non-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Exposer le port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')"

# Commande par défaut (sera overridée par docker-compose)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

### backend/.dockerignore

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.git
.gitignore
README.md
*.md
.vscode/
.idea/
*.sqlite3
db.sqlite3
media/
staticfiles/
```

---

### backend/requirements.txt

```txt
# Django
Django==5.0.1
djangorestframework==3.14.0
django-cors-headers==4.3.1

# Database
psycopg2-binary==2.9.9

# Authentication
djangorestframework-simplejwt==5.3.1
py-webauthn==2.0.0

# Utilities
python-dotenv==1.0.0
gunicorn==21.2.0
whitenoise==6.6.0

# Date/Time
python-dateutil==2.8.2

# Validation
django-filter==23.5
```

---

### frontend/Dockerfile

```dockerfile
# Stage 1: Build
FROM node:20-alpine as builder

WORKDIR /app

# Copier package files
COPY package*.json ./

# Installer les dépendances
RUN npm ci --only=production

# Copier le code source
COPY . .

# Build argument pour l'API base URL
ARG NUXT_PUBLIC_API_BASE
ENV NUXT_PUBLIC_API_BASE=${NUXT_PUBLIC_API_BASE}

# Build de l'application
RUN npm run build

# Stage 2: Production
FROM node:20-alpine as production

WORKDIR /app

# Copier les fichiers nécessaires depuis le builder
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/package*.json ./

# Installer uniquement les dépendances de production
RUN npm ci --only=production

# Créer un utilisateur non-root
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown -R appuser:appuser /app

USER appuser

# Exposer le port
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Démarrer l'application
CMD ["node", ".output/server/index.mjs"]
```

---

### frontend/.dockerignore

```
node_modules/
.nuxt/
.output/
dist/
.git/
.gitignore
README.md
*.md
.vscode/
.idea/
.env
.env.*
!.env.example
```

---

### nginx/nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logs
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/json application/javascript;

    # Upstream servers
    upstream frontend {
        server frontend:3000;
    }

    upstream backend {
        server backend:8000;
    }

    # HTTP Server
    server {
        listen 80;
        server_name _;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Client body size
        client_max_body_size 10M;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # Media files
        location /media/ {
            alias /var/www/media/;
            expires 7d;
        }
    }

    # HTTPS Server (à configurer avec vos certificats SSL)
    # server {
    #     listen 443 ssl http2;
    #     server_name votre-domaine.com;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers HIGH:!aNULL:!MD5;
    #
    #     # Même configuration que HTTP
    # }
}
```

---

## Variables d'environnement

### .env.example

```bash
# ======================
# GÉNÉRAL
# ======================
COMPOSE_PROJECT_NAME=budget-tracker
DEBUG=False

# ======================
# BACKEND (Django)
# ======================
SECRET_KEY=votre-secret-key-tres-longue-et-securisee
ALLOWED_HOSTS=localhost,127.0.0.1,raspberrypi.local
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://raspberrypi.local:3000

# JWT
JWT_ACCESS_TOKEN_LIFETIME=15  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # jours

# ======================
# BASE DE DONNÉES
# ======================
POSTGRES_DB=budget_db
POSTGRES_USER=budget_user
POSTGRES_PASSWORD=votre-mot-de-passe-securise

# ======================
# FRONTEND (Nuxt)
# ======================
NUXT_PUBLIC_API_BASE=http://localhost:8000/api/v1

# ======================
# NGINX
# ======================
# Décommenter pour utiliser Nginx
# NGINX_PORT=80
# NGINX_SSL_PORT=443
```

### Générer un SECRET_KEY sécurisé

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## Installation sur Raspberry Pi

### 1. Préparer le Raspberry Pi

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer les dépendances
sudo apt install -y git curl

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Installer Docker Compose
sudo apt install -y docker-compose

# Redémarrer pour appliquer les changements
sudo reboot
```

### 2. Cloner le projet

```bash
# Cloner le repository
git clone https://github.com/votre-utilisateur/budget-tracker.git
cd budget-tracker
```

### 3. Configurer les variables d'environnement

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env
nano .env

# Générer et ajouter un SECRET_KEY sécurisé
# Modifier les mots de passe
# Ajuster les URLs selon votre configuration
```

### 4. Construire et lancer les containers

```bash
# Construction des images
docker-compose build

# Lancer tous les services
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps
```

### 5. Initialiser la base de données

```bash
# Appliquer les migrations
docker-compose exec backend python manage.py migrate

# Créer un superutilisateur
docker-compose exec backend python manage.py createsuperuser

# Charger les catégories par défaut (si vous avez un fixture)
docker-compose exec backend python manage.py loaddata categories
```

### 6. Vérifier l'installation

```bash
# Vérifier le frontend
curl http://localhost:3000

# Vérifier le backend
curl http://localhost:8000/api/v1/

# Vérifier la base de données
docker-compose exec database psql -U budget_user -d budget_db -c "\dt"
```

---

## Commandes utiles

### Gestion des containers

```bash
# Démarrer tous les services
docker-compose up -d

# Arrêter tous les services
docker-compose down

# Redémarrer un service spécifique
docker-compose restart backend

# Voir les logs
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f backend

# Voir l'utilisation des ressources
docker stats
```

### Gestion de la base de données

```bash
# Accéder au shell PostgreSQL
docker-compose exec database psql -U budget_user -d budget_db

# Créer un backup
docker-compose exec database pg_dump -U budget_user budget_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurer un backup
docker-compose exec -T database psql -U budget_user -d budget_db < backup_20260203_120000.sql

# Voir la taille de la base de données
docker-compose exec database psql -U budget_user -d budget_db -c "SELECT pg_size_pretty(pg_database_size('budget_db'));"
```

### Gestion Django

```bash
# Exécuter des migrations
docker-compose exec backend python manage.py migrate

# Créer des migrations
docker-compose exec backend python manage.py makemigrations

# Ouvrir le shell Django
docker-compose exec backend python manage.py shell

# Collecter les fichiers statiques
docker-compose exec backend python manage.py collectstatic --noinput

# Créer un superutilisateur
docker-compose exec backend python manage.py createsuperuser
```

### Nettoyage

```bash
# Supprimer tous les containers arrêtés
docker container prune

# Supprimer toutes les images inutilisées
docker image prune -a

# Supprimer tous les volumes inutilisés (ATTENTION : perte de données)
docker volume prune

# Nettoyage complet du système Docker
docker system prune -a --volumes
```

---

## Backup et restauration

### Script de backup automatique

Créer un fichier `scripts/backup.sh` :

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/home/pi/budget-tracker/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Créer le répertoire de backup s'il n'existe pas
mkdir -p $BACKUP_DIR

# Backup de la base de données
echo "Creating database backup..."
docker-compose exec -T database pg_dump -U budget_user budget_db | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup des fichiers media (si utilisés)
echo "Creating media backup..."
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz backend/media/

# Supprimer les backups de plus de X jours
echo "Cleaning old backups..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
```

Rendre le script exécutable :

```bash
chmod +x scripts/backup.sh
```

### Automatiser les backups avec cron

```bash
# Éditer la crontab
crontab -e

# Ajouter cette ligne pour un backup quotidien à 2h du matin
0 2 * * * /home/pi/budget-tracker/scripts/backup.sh >> /home/pi/budget-tracker/logs/backup.log 2>&1
```

### Restauration

```bash
# Restaurer la base de données
gunzip -c backups/db_backup_20260203_120000.sql.gz | docker-compose exec -T database psql -U budget_user -d budget_db

# Restaurer les fichiers media
tar -xzf backups/media_backup_20260203_120000.tar.gz -C backend/
```

---

## Monitoring

### Vérifier l'état de santé

```bash
# État des containers
docker-compose ps

# Utilisation des ressources
docker stats --no-stream

# Logs des dernières erreurs
docker-compose logs --tail=100 | grep -i error
```

### Surveiller l'espace disque

```bash
# Espace disque total
df -h

# Espace utilisé par Docker
docker system df

# Espace utilisé par les volumes
docker volume ls -q | xargs docker volume inspect | grep Mountpoint | awk '{print $2}' | xargs du -sh
```

### Healthchecks

Vérifier les healthchecks des containers :

```bash
docker inspect --format='{{json .State.Health}}' budget_backend | jq
docker inspect --format='{{json .State.Health}}' budget_frontend | jq
```

### Monitoring avec Portainer (optionnel)

```bash
# Installer Portainer
docker volume create portainer_data
docker run -d -p 9000:9000 --name=portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce

# Accéder à Portainer
# http://raspberrypi.local:9000
```

---

## Mise à jour

### Mettre à jour l'application

```bash
# Récupérer les dernières modifications
git pull origin main

# Reconstruire les images si nécessaire
docker-compose build

# Arrêter les services
docker-compose down

# Créer un backup avant la mise à jour
./scripts/backup.sh

# Démarrer avec les nouvelles images
docker-compose up -d

# Appliquer les nouvelles migrations
docker-compose exec backend python manage.py migrate

# Vérifier que tout fonctionne
docker-compose logs -f
```

### Rollback en cas de problème

```bash
# Retourner à la version précédente du code
git checkout <commit-hash>

# Reconstruire et relancer
docker-compose down
docker-compose build
docker-compose up -d

# Restaurer un backup si nécessaire
gunzip -c backups/db_backup_YYYYMMDD_HHMMSS.sql.gz | docker-compose exec -T database psql -U budget_user -d budget_db
```

---

## Troubleshooting

### Le container backend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs backend

# Problèmes courants :
# 1. Base de données pas prête → attendre quelques secondes
# 2. Migrations non appliquées → docker-compose exec backend python manage.py migrate
# 3. SECRET_KEY manquant → vérifier le fichier .env
```

### Le container frontend ne démarre pas

```bash
# Vérifier les logs
docker-compose logs frontend

# Reconstruire l'image
docker-compose build frontend
docker-compose up -d frontend
```

### Erreur de connexion à la base de données

```bash
# Vérifier que le container database est en cours d'exécution
docker-compose ps database

# Vérifier la santé de la base de données
docker-compose exec database pg_isready -U budget_user

# Vérifier les credentials dans .env
cat .env | grep POSTGRES
```

### Problèmes de performance sur Raspberry Pi

```bash
# Réduire le nombre de workers Gunicorn
# Dans docker-compose.yml, changer --workers 2 en --workers 1

# Limiter la mémoire des containers
# Ajouter dans docker-compose.yml sous chaque service :
# deploy:
#   resources:
#     limits:
#       memory: 512M

# Optimiser PostgreSQL pour Raspberry Pi
# Créer un fichier postgresql.conf avec :
# shared_buffers = 128MB
# effective_cache_size = 512MB
# maintenance_work_mem = 64MB
# work_mem = 4MB
```

### Espace disque insuffisant

```bash
# Nettoyer Docker
docker system prune -a

# Supprimer les vieux backups
find backups/ -mtime +30 -delete

# Supprimer les logs volumineux
docker-compose logs --tail=0 -f > /dev/null 2>&1
truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

### Impossible d'accéder à l'application depuis un autre appareil

```bash
# Vérifier que les ports sont bien exposés
docker-compose ps

# Vérifier le firewall
sudo ufw status
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 80/tcp

# Obtenir l'IP du Raspberry Pi
hostname -I

# Tester depuis un autre appareil
curl http://<raspberry-pi-ip>:3000
```

---

## Sécurité

### Recommandations

1. **Changer tous les mots de passe par défaut**
2. **Utiliser HTTPS en production** (Let's Encrypt)
3. **Configurer le firewall** (ufw)
4. **Mettre à jour régulièrement** le système et les images Docker
5. **Limiter l'accès SSH** au Raspberry Pi
6. **Activer les backups automatiques**
7. **Surveiller les logs** régulièrement

### Configurer HTTPS avec Let's Encrypt

```bash
# Installer certbot
sudo apt install certbot

# Obtenir un certificat
sudo certbot certonly --standalone -d votre-domaine.com

# Les certificats seront dans /etc/letsencrypt/live/votre-domaine.com/

# Configurer le renouvellement automatique
sudo crontab -e
# Ajouter : 0 3 * * * certbot renew --quiet
```

---

## Optimisations pour Raspberry Pi

### Réduire l'utilisation de la mémoire

```yaml
# Dans docker-compose.yml, ajouter pour chaque service :
deploy:
  resources:
    limits:
      memory: 512M
    reservations:
      memory: 256M
```

### Utiliser un SSD au lieu d'une carte SD

- Meilleure performance
- Plus de durabilité
- Moins de risque de corruption

### Overclocker le Raspberry Pi (optionnel)

```bash
# Éditer /boot/config.txt
sudo nano /boot/config.txt

# Ajouter (pour Raspberry Pi 4)
over_voltage=6
arm_freq=2000

# Redémarrer
sudo reboot
```

---

## Support et logs

### Collecter les informations de debug

```bash
# Créer un fichier avec toutes les informations utiles
echo "=== Docker version ===" > debug_info.txt
docker --version >> debug_info.txt
echo "=== Docker Compose version ===" >> debug_info.txt
docker-compose --version >> debug_info.txt
echo "=== Containers status ===" >> debug_info.txt
docker-compose ps >> debug_info.txt
echo "=== Backend logs ===" >> debug_info.txt
docker-compose logs --tail=100 backend >> debug_info.txt
echo "=== Frontend logs ===" >> debug_info.txt
docker-compose logs --tail=100 frontend >> debug_info.txt
echo "=== Database logs ===" >> debug_info.txt
docker-compose logs --tail=100 database >> debug_info.txt
```

---

## À compléter

- [ ] Configuration SSL/TLS complète
- [ ] Monitoring avancé avec Prometheus/Grafana
- [ ] CI/CD pipeline
- [ ] Tests automatisés avant déploiement
- [ ] Documentation pour mise à l'échelle (multi-instance)
