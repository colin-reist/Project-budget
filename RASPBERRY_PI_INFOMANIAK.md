# 🍓 Déploiement Raspberry Pi + Caddy + Infomaniak

Guide complet pour déployer Budget Tracker sur un Raspberry Pi avec Caddy comme reverse proxy et DNS chez Infomaniak.

## 📋 Architecture Finale

```
Internet
   ↓ (Infomaniak DNS)
   ↓ (yourdomain.com → IP du RPi)
   ↓
Caddy (port 80/443)
   ↓ reverse proxy
   ├─→ Frontend Nuxt (port 3000)
   └─→ Backend Django (port 8000)
   ↓
Docker Containers
   ├─→ PostgreSQL (persistant)
   ├─→ Django (API)
   └─→ Nuxt (Frontend)
```

## 🚀 Étape 1: Installation de Base (Raspberry Pi)

### 1.1 Préparation du Raspberry Pi

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer les dépendances essentielles
sudo apt install -y \
  curl \
  git \
  wget \
  build-essential \
  libssl-dev \
  libffi-dev \
  python3-dev

# Vérifier la capacité disque (recommandé 16GB+)
df -h /

# Vérifier la RAM (recommandé 2GB+)
free -h
```

### 1.2 Installation de Docker

```bash
# Installer Docker
curl -sSL https://get.docker.com | sh

# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER
newgrp docker

# Vérifier
docker --version
docker run hello-world
```

### 1.3 Installation de Docker Compose

```bash
# Installer Docker Compose
sudo apt install -y docker-compose

# Vérifier
docker-compose --version
```

### 1.4 Installation de Caddy

```bash
# Installer Caddy
sudo apt install -y caddy

# Vérifier
caddy version

# Démarrer Caddy
sudo systemctl start caddy
sudo systemctl enable caddy

# Vérifier le statut
sudo systemctl status caddy
```

## 🌐 Étape 2: Configuration Infomaniak DNS

### 2.1 Accéder au Panneau Infomaniak

1. Aller sur https://www.infomaniak.com
2. Connexion à votre compte
3. Domaines → Gérer les domaines → Cliquer sur votre domaine

### 2.2 Configuration des Enregistrements DNS

#### Récupérer l'IP de votre Raspberry Pi

```bash
# Depuis le RPi
hostname -I

# Résultat exemple: 192.168.1.100
# (pour accès interne) ou IP publique (pour accès externe)
```

#### Ajouter les Enregistrements dans Infomaniak

**A) Enregistrement A (IPv4)**

| Type | Nom | Valeur | TTL |
|------|-----|--------|-----|
| A | @ | 192.168.1.100* | 3600 |
| A | www | 192.168.1.100* | 3600 |

*Remplacer par votre IP publique ou domaine avec port forwarding

**B) Enregistrement AAAA (IPv6)** (optionnel)

Si vous avez une adresse IPv6 de votre FAI:

| Type | Nom | Valeur | TTL |
|------|-----|--------|-----|
| AAAA | @ | 2001:db8::1* | 3600 |
| AAAA | www | 2001:db8::1* | 3600 |

*Remplacer par votre IPv6

### 2.3 Vérifier la Propagation DNS

```bash
# Depuis votre ordinateur
nslookup yourdomain.com
# ou
dig yourdomain.com

# Depuis le RPi
host yourdomain.com
ping yourdomain.com

# Attendre quelques minutes pour la propagation (généralement 5-15 min)
```

## 🏠 Étape 3: Port Forwarding (Si Accès de l'Extérieur)

Si vous accédez depuis l'extérieur de votre réseau:

1. Aller dans la configuration de votre routeur (192.168.1.1 ou 192.168.0.1)
2. Trouver "Port Forwarding" ou "Redirection de ports"
3. Ajouter:
   - **Port externe**: 80 → **Port interne**: 80 (RPi)
   - **Port externe**: 443 → **Port interne**: 443 (RPi)
   - **Adresse IP interne**: 192.168.1.100 (IP du RPi)

## 🐳 Étape 4: Configuration Docker sur RPi

### 4.1 Cloner le Projet

```bash
# Créer un répertoire
mkdir -p /home/pi/apps
cd /home/pi/apps

# Cloner le projet
git clone https://github.com/votre-username/Project-budget.git
cd Project-budget
```

### 4.2 Configurer l'Environnement

```bash
# Copier le template
cp .env.example .env

# Éditer la configuration
nano .env
```

**Contenu à modifier dans .env:**

```env
# Environnement
DEBUG=False
COMPOSE_PROJECT_NAME=budget-tracker

# Sécurité - Générer une clé
# python -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY=VOTRE_CLÉ_GÉNÉRÉE_ICI

# DNS / Domaine
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Base de données
POSTGRES_DB=budget_db
POSTGRES_USER=budget_user
POSTGRES_PASSWORD=VOTRE_MOT_DE_PASSE_FORT_ICI

# WebAuthn
WEBAUTHN_RP_ID=yourdomain.com
WEBAUTHN_RP_NAME=Budget Tracker
WEBAUTHN_ORIGIN=https://yourdomain.com

# API Frontend
NUXT_PUBLIC_API_BASE=https://yourdomain.com/api/v1
```

### 4.3 Lancer l'Application

```bash
# Démarrer les conteneurs
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps

# Vérifier les logs
docker-compose logs -f backend
```

### 4.4 Vérifier l'Accessibilité

```bash
# Depuis le RPi
curl http://localhost:3000
curl http://localhost:8000/api/v1/

# Depuis votre ordinateur
curl http://192.168.1.100:3000
curl http://192.168.1.100:8000
```

## 🔐 Étape 5: Configuration Caddy

### 5.1 Créer le Caddyfile

```bash
# Éditer la configuration Caddy
sudo nano /etc/caddy/Caddyfile
```

**Contenu du Caddyfile:**

```caddy
# Configuration Caddy pour Budget Tracker
# Remplacer yourdomain.com par votre domaine

yourdomain.com, www.yourdomain.com {
    # Compression
    encode gzip

    # Logs
    log {
        output file /var/log/caddy/access.log {
            roll_size 100mb
            roll_keep 10
            roll_keep_for 720h
        }
        format json
    }

    # Reverse proxy pour le Frontend (port 3000)
    handle_path /app* {
        reverse_proxy localhost:3000 {
            header_uri -X-Forwarded-Proto https
            header_uri -X-Forwarded-For {http.request.remote.host}
        }
    }

    # Reverse proxy pour l'API (port 8000)
    handle_path /api* {
        reverse_proxy localhost:8000 {
            header_uri -X-Forwarded-Proto https
            header_uri -X-Forwarded-For {http.request.remote.host}
        }
    }

    # Redirection root vers le frontend
    handle / {
        reverse_proxy localhost:3000 {
            header_uri -X-Forwarded-Proto https
            header_uri -X-Forwarded-For {http.request.remote.host}
        }
    }

    # Cache statique
    @static {
        path *.css *.js *.png *.jpg *.gif *.svg *.woff *.woff2
    }
    header @static Cache-Control "public, max-age=31536000"

    # Sécurité
    header Referrer-Policy "no-referrer-when-downgrade"
    header X-Content-Type-Options "nosniff"
    header X-Frame-Options "SAMEORIGIN"
    header X-XSS-Protection "1; mode=block"
}
```

### 5.2 Valider et Appliquer la Configuration

```bash
# Valider la syntaxe
caddy validate --config /etc/caddy/Caddyfile

# Redémarrer Caddy
sudo systemctl restart caddy

# Vérifier le statut
sudo systemctl status caddy

# Vérifier les logs
sudo tail -50 /var/log/caddy/access.log
```

### 5.3 Certificat SSL Let's Encrypt (Automatique)

Caddy gère automatiquement les certificats SSL avec Let's Encrypt!

```bash
# Vérifier les certificats
sudo ls -la /var/lib/caddy/

# Voir les logs de Caddy
sudo journalctl -u caddy -f
```

**Caddy va:**
- ✅ Détecter votre domaine dans le Caddyfile
- ✅ Demander un certificat à Let's Encrypt
- ✅ Configurer HTTPS automatiquement
- ✅ Renouveler le certificat avant expiration

## 🔗 Étape 6: Configuration Frontend

### 6.1 Modifier la Configuration Nuxt

```bash
# Éditer le fichier de configuration
nano /home/pi/apps/Project-budget/frontend/nuxt.config.ts
```

**Vérifier que l'API base est correcte:**

```typescript
export default defineNuxtConfig({
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'https://yourdomain.com/api/v1'
    }
  },
  // ... reste de la config
})
```

### 6.2 Reconstruire le Frontend

```bash
cd /home/pi/apps/Project-budget

# Mettre à jour le frontend
docker-compose build frontend
docker-compose up -d frontend

# Vérifier
docker-compose logs frontend | tail -20
```

## 🧪 Étape 7: Tests et Vérification

### 7.1 Test HTTPS

```bash
# Depuis le RPi
curl -I https://yourdomain.com

# Depuis votre ordinateur
curl -I https://yourdomain.com

# Vérifier le certificat
openssl s_client -connect yourdomain.com:443 -showcerts
```

**Résultat attendu:**
```
HTTP/2 200
certificate verify OK
issuer=C=US,O=Let's Encrypt
```

### 7.2 Test des Services

```bash
# Frontend
curl -I https://yourdomain.com

# API
curl -I https://yourdomain.com/api/v1/

# Status de la base de données
curl -I https://yourdomain.com/api/v1/accounts/

# Tous les services doivent retourner HTTP 200 ou 30x (redirection)
```

### 7.3 Accès Depuis Navigateur

1. Ouvrir https://yourdomain.com
2. Vérifier que le certificat est valide (🔒 vert)
3. S'enregistrer et tester l'application

## 📊 Étape 8: Monitoring et Maintenance

### 8.1 Vérifier l'État Régulièrement

```bash
# État des conteneurs
docker-compose ps

# Utilisation des ressources
docker stats

# Espace disque
df -h

# Logs du backend
docker-compose logs -f backend

# Logs de Caddy
sudo tail -f /var/log/caddy/access.log
```

### 8.2 Sauvegarde Automatique

```bash
# Créer le répertoire de backup
mkdir -p /home/pi/apps/Project-budget/backups

# Créer un script de backup
cat > /home/pi/backup-db.sh << 'EOF'
#!/bin/bash
cd /home/pi/apps/Project-budget
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T database pg_dump -U budget_user budget_db > backups/backup_${DATE}.sql
echo "Backup créé: backups/backup_${DATE}.sql"

# Garder seulement les 30 derniers backups
cd backups
ls -t | tail -n +31 | xargs -r rm
EOF

chmod +x /home/pi/backup-db.sh

# Ajouter au cron (backup quotidien à 2h du matin)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/pi/backup-db.sh") | crontab -

# Vérifier
crontab -l
```

### 8.3 Mise à Jour de l'Application

```bash
cd /home/pi/apps/Project-budget

# Récupérer les modifications
git pull origin main

# Reconstruire et redémarrer
docker-compose build
docker-compose up -d

# Vérifier
docker-compose ps
docker-compose logs -f backend
```

## 🔐 Sécurité

### 8.4 Firewall (optionnel mais recommandé)

```bash
# Installer UFW
sudo apt install -y ufw

# Autoriser SSH
sudo ufw allow 22/tcp

# Autoriser HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activer le firewall
sudo ufw enable

# Vérifier
sudo ufw status
```

### 8.5 Certificat SSL - Renouvellement Automatique

Caddy gère automatiquement le renouvellement. Vérifier:

```bash
# Logs de renouvellement
sudo journalctl -u caddy | grep -i renew

# Date d'expiration du certificat
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

## 📱 Accès depuis l'Extérieur

### À partir de votre ordinateur

```bash
# Si sur le même réseau Wi-Fi
https://yourdomain.com

# Si sur réseau différent (4G, autre Wi-Fi)
https://yourdomain.com (port forwarding nécessaire)
```

### À partir de votre téléphone

```
Ouvrir un navigateur → https://yourdomain.com
Ajouter un raccourci à l'écran d'accueil
→ Application web progressive (PWA)
```

## 🆘 Dépannage

### Caddy ne démarre pas

```bash
# Vérifier les erreurs
sudo systemctl status caddy
sudo journalctl -u caddy -f

# Valider la configuration
sudo caddy validate --config /etc/caddy/Caddyfile

# Redémarrer
sudo systemctl restart caddy
```

### DNS ne résout pas

```bash
# Vérifier dans Infomaniak
# 1. Panneau → Domaines → DNS
# 2. Vérifier que A et AAAA (optionnel) pointent vers l'IP du RPi
# 3. Attendre la propagation DNS (5-15 min)

# Tester manuellement
nslookup yourdomain.com 8.8.8.8
dig yourdomain.com +short
```

### HTTPS ne fonctionne pas

```bash
# Vérifier les certificats
sudo ls -la /var/lib/caddy/

# Vérifier les logs
sudo journalctl -u caddy -f

# Tester la validité
curl -v https://yourdomain.com
```

### Application lente

```bash
# Vérifier la mémoire
free -h

# Vérifier le CPU
top -bn1 | head -20

# Vérifier l'espace disque
df -h

# Réduire les ressources Docker si nécessaire
# Éditer docker-compose.yml et ajouter des limites
```

## 📚 Fichiers Importants

| Fichier | Localisation | Objectif |
|---------|--------------|----------|
| .env | ~/apps/Project-budget/ | Configuration application |
| Caddyfile | /etc/caddy/ | Configuration reverse proxy |
| docker-compose.yml | ~/apps/Project-budget/ | Configuration Docker |
| Certificats SSL | /var/lib/caddy/ | Certificats Let's Encrypt |
| Logs Caddy | /var/log/caddy/ | Logs d'accès |
| Backups BD | ~/apps/Project-budget/backups/ | Sauvegardes PostgreSQL |

## 🎯 Résumé des Commandes Essentielles

```bash
# Gestion application
cd /home/pi/apps/Project-budget
docker-compose ps                          # État
docker-compose logs -f backend             # Logs
docker-compose restart backend             # Redémarrer
docker-compose down                        # Arrêter (données conservées)

# Gestion Caddy
sudo systemctl status caddy                # État
sudo systemctl restart caddy               # Redémarrer
sudo journalctl -u caddy -f                # Logs
sudo caddy validate --config /etc/caddy/Caddyfile  # Valider config

# Sauvegarde
/home/pi/backup-db.sh                      # Backup manuel
ls -la /home/pi/apps/Project-budget/backups/  # Voir backups

# Mises à jour
git pull origin main && docker-compose build && docker-compose up -d
```

## ✨ Avantages de cette Configuration

✅ **HTTPS automatique** - Let's Encrypt via Caddy
✅ **Reverse proxy simple** - Caddy vs Nginx
✅ **DNS chez Infomaniak** - Facile à gérer
✅ **Données persistantes** - Docker volumes
✅ **Mises à jour sans perte** - Redémarrage transparent
✅ **Sauvegarde automatique** - Cron quotidien
✅ **Sécurisé** - Firewall + HTTPS + SSL/TLS
✅ **24/7 disponible** - Raspberry Pi économe
✅ **Accès interne et externe** - Réseau local + Internet

## 🚀 Prochaines Étapes

1. ✅ Tester l'application: https://yourdomain.com
2. ✅ Créer un utilisateur
3. ✅ Ajouter des comptes et transactions
4. ✅ Vérifier les sauvegardes automatiques
5. ✅ Moniter les performances

**Vous avez maintenant un serveur personnel sécurisé et professionnel! 🎉**
