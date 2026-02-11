# 🚀 Docker Quick Start

Démarrer et mettre à jour l'application en 3 commandes.

## ⚡ Installation Initiale (Une fois)

```bash
# 1. Créer la configuration
cp .env.example .env

# 2. Éditer .env et générer une clé
python -c "import secrets; print(secrets.token_urlsafe(50))"
# Copier la clé générée dans SECRET_KEY

# 3. Lancer l'application
docker-compose up -d
```

✅ Application ready: http://localhost:3000

## 🔄 Mise à Jour (Sans Perte de Données)

### Windows
```bash
deploy.bat
# Choisir l'option 1 pour déploiement complet
```

### Linux/Mac
```bash
./deploy.sh deploy
# ou deploy-frontend, deploy-backend
```

### Manuel
```bash
git pull origin main
docker-compose build
docker-compose up -d
```

## 📊 Commandes Utiles

```bash
# État
docker-compose ps

# Logs
docker-compose logs -f backend

# Arrêter (données conservées)
docker-compose down

# Sauvegarde
docker-compose exec database pg_dump -U budget_user budget_db > backup.sql

# Restaurer
docker-compose exec -T database psql -U budget_user budget_db < backup.sql
```

## 🎯 Résumé

| Situation | Commande | Données |
|-----------|----------|---------|
| Première démarrage | `docker-compose up -d` | Safe |
| Update frontend | `docker-compose build frontend && docker-compose up -d frontend` | ✅ Preserved |
| Update backend | `docker-compose build backend && docker-compose up -d backend` | ✅ Preserved |
| Update tout | `docker-compose build && docker-compose up -d` | ✅ Preserved |
| Arrêter | `docker-compose down` | ✅ Preserved |
| Reset complet ⚠️ | `docker-compose down -v` | ❌ DELETED |

👉 **Les données persisten tant que vous n'ajoutez pas `-v` à down!**

Pour plus de détails → **DOCKER.md**
