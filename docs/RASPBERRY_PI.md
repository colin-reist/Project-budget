# 🍓 Déploiement sur Raspberry Pi

Guide complet pour déployer Budget Tracker sur un Raspberry Pi avec Caddy comme reverse proxy et DNS chez Infomaniak.

---

## 📋 Table des Matières

- [Architecture](#-architecture-finale)
- [Installation Rapide (Automatisée)](#-installation-rapide-automatisée)
- [Installation Manuelle (Complète)](#-installation-manuelle-complète)
- [Configuration DNS Infomaniak](#-configuration-dns-infomaniak)
- [Configuration Caddy](#-configuration-caddy)
- [Tests et Vérification](#-tests-et-vérification)
- [Monitoring et Maintenance](#-monitoring-et-maintenance)
- [Dépannage](#-dépannage)

---

## 📐 Architecture Finale

```
Internet
   ↓ (Infomaniak DNS)
   ↓ (yourdomain.com → IP du RPi)
   ↓
Caddy (port 80/443)
   ↓ reverse proxy + HTTPS automatique
   ├─→ Frontend Nuxt (port 3000)
   └─→ Backend Django (port 8000)
   ↓
Docker Containers
   ├─→ PostgreSQL (persistant)
   ├─→ Django (API)
   └─→ Nuxt (Frontend)
```

---

## ⚡ Installation Rapide (Automatisée)

### Prérequis

- Raspberry Pi 4 (4GB RAM recommandé)
- Raspberry Pi OS installé
- Connexion Internet
- Domaine chez Infomaniak (ou autre)

### Installation en 3 Commandes

```bash
# 1. SSH sur le Raspberry Pi
ssh pi@raspberrypi.local
# ou: ssh pi@192.168.1.100

# 2. Cloner et lancer l'installation automatisée
git clone https://github.com/votre-username/Project-budget.git
cd Project-budget
sudo bash scripts/install-rpi.sh

# 3. Suivre les instructions à l'écran
```

### Que fait le script d'installation ?

Le script `install-rpi.sh` installe automatiquement:

✅ Docker et Docker Compose
✅ Caddy (reverse proxy)
✅ Configuration du firewall (UFW)
✅ Clone du projet dans `/home/pi/apps/Project-budget`
✅ Création du fichier `.env`
✅ Configuration des backups automatiques
✅ Lancement de l'application

### Configuration Post-Installation

Après l'installation automatisée, vous devrez configurer:

#### 1️⃣ Éditer `.env`

```bash
nano /home/pi/apps/Project-budget/.env
```

Modifier ces lignes:

```env
# Votre domaine réel
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Mot de passe fort pour la BD (changez-le!)
POSTGRES_PASSWORD=VotreMotDePasseFortIci123!

# WebAuthn
WEBAUTHN_RP_ID=yourdomain.com
WEBAUTHN_RP_NAME=Budget Tracker
WEBAUTHN_ORIGIN=https://yourdomain.com

# API
NUXT_PUBLIC_API_BASE=https://yourdomain.com/api/v1
```

Sauvegarder: `Ctrl+O`, `Entrée`, `Ctrl+X`

#### 2️⃣ Éditer `Caddyfile`

```bash
sudo nano /etc/caddy/Caddyfile
```

Remplacer **tous** les `yourdomain.com` par votre domaine réel.

Sauvegarder: `Ctrl+O`, `Entrée`, `Ctrl+X`

#### 3️⃣ Redémarrer les services

```bash
# Redémarrer Caddy
sudo systemctl restart caddy

# Redémarrer l'application
cd /home/pi/apps/Project-budget
docker-compose restart
```

---

## 🔧 Installation Manuelle (Complète)

Si vous préférez installer manuellement ou comprendre chaque étape:

### Étape 1: Préparation du Raspberry Pi

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

### Étape 2: Installation de Docker

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

### Étape 3: Installation de Docker Compose

```bash
# Installer Docker Compose
sudo apt install -y docker-compose

# Vérifier
docker-compose --version
```

### Étape 4: Installation de Caddy

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

### Étape 5: Cloner et Configurer le Projet

```bash
# Créer un répertoire
mkdir -p /home/pi/apps
cd /home/pi/apps

# Cloner le projet
git clone https://github.com/votre-username/Project-budget.git
cd Project-budget

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

### Étape 6: Lancer l'Application

```bash
# Démarrer les conteneurs
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps

# Appliquer les migrations
docker-compose exec backend python manage.py migrate

# Créer un superutilisateur
docker-compose exec backend python manage.py createsuperuser

# Vérifier les logs
docker-compose logs -f backend
```

---

## 🌐 Configuration DNS Infomaniak

### Accéder au Panneau Infomaniak

1. Aller sur https://www.infomaniak.com
2. Connexion → Domaines → Gérer les domaines → Votre domaine
3. Onglet "DNS" ou "Enregistrements DNS"

### Récupérer l'IP du Raspberry Pi

```bash
# Depuis le RPi
hostname -I

# Résultat exemple: 192.168.1.100
```

### Ajouter les Enregistrements DNS

#### A) Accès Local (Réseau Wi-Fi)

| Type | Nom | Valeur | TTL |
|------|-----|--------|-----|
| **A** | @ | 192.168.1.100 | 3600 |
| **A** | www | 192.168.1.100 | 3600 |

#### B) Accès Externe (Internet)

| Type | Nom | Valeur | TTL |
|------|-----|--------|-----|
| **A** | @ | VOTRE_IP_PUBLIQUE | 3600 |
| **A** | www | VOTRE_IP_PUBLIQUE | 3600 |

**Trouver votre IP publique:**
```bash
curl ifconfig.me
# ou
curl icanhazip.com
```

#### C) IPv6 (Optionnel)

Si vous avez une adresse IPv6:

| Type | Nom | Valeur | TTL |
|------|-----|--------|-----|
| **AAAA** | @ | votre:ipv6:ici | 3600 |
| **AAAA** | www | votre:ipv6:ici | 3600 |

### Vérifier la Propagation DNS

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

---

## 🏠 Port Forwarding (Pour Accès Externe)

Si vous accédez depuis l'extérieur de votre réseau local:

1. Accéder à votre routeur (généralement 192.168.1.1 ou 192.168.0.1)
2. Trouver "Port Forwarding" ou "Redirection de ports"
3. Ajouter les règles:
   - **Port externe**: 80 → **Port interne**: 80 (IP du RPi)
   - **Port externe**: 443 → **Port interne**: 443 (IP du RPi)
   - **Adresse IP interne**: 192.168.1.100 (IP du RPi)

---

## 🔐 Configuration Caddy

### Créer le Caddyfile

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
            header_up X-Forwarded-Proto https
            header_up X-Forwarded-For {http.request.remote.host}
        }
    }

    # Reverse proxy pour l'API (port 8000)
    handle_path /api* {
        reverse_proxy localhost:8000 {
            header_up X-Forwarded-Proto https
            header_up X-Forwarded-For {http.request.remote.host}
        }
    }

    # Redirection root vers le frontend
    handle / {
        reverse_proxy localhost:3000 {
            header_up X-Forwarded-Proto https
            header_up X-Forwarded-For {http.request.remote.host}
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

### Valider et Appliquer la Configuration

```bash
# Valider la syntaxe
caddy validate --config /etc/caddy/Caddyfile

# Redémarrer Caddy
sudo systemctl restart caddy

# Vérifier le statut
sudo systemctl status caddy

# Vérifier les logs
sudo journalctl -u caddy -f
```

### Certificat SSL Let's Encrypt (Automatique)

Caddy gère automatiquement les certificats SSL avec Let's Encrypt!

```bash
# Vérifier les certificats
sudo ls -la /var/lib/caddy/

# Voir les logs de Caddy
sudo journalctl -u caddy -f
```

**Caddy va automatiquement:**
- ✅ Détecter votre domaine dans le Caddyfile
- ✅ Demander un certificat à Let's Encrypt
- ✅ Configurer HTTPS automatiquement
- ✅ Renouveler le certificat avant expiration

---

## 🧪 Tests et Vérification

### Test HTTPS

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

### Test des Services

```bash
# Frontend
curl -I https://yourdomain.com

# API
curl -I https://yourdomain.com/api/v1/

# Admin Django
curl -I https://yourdomain.com/admin/

# Tous les services doivent retourner HTTP 200 ou 30x (redirection)
```

### Accès Depuis Navigateur

1. Ouvrir https://yourdomain.com
2. Vérifier que le certificat est valide (🔒 vert)
3. S'enregistrer et tester l'application

---

## 📊 Monitoring et Maintenance

### Vérifier l'État Régulièrement

```bash
# État des conteneurs
docker-compose ps

# Utilisation des ressources
docker stats

# Espace disque
df -h

# Mémoire
free -h

# Logs du backend
docker-compose logs -f backend

# Logs de Caddy
sudo tail -f /var/log/caddy/access.log
```

### Sauvegarde Automatique

La sauvegarde automatique est configurée par le script d'installation. Sinon:

```bash
# Créer le répertoire de backup
mkdir -p /home/pi/apps/Project-budget/backups

# Le script de backup est déjà dans scripts/backup.sh
# Ou créer manuellement:
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

### Mise à Jour de l'Application

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

### Firewall (UFW)

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

### Certificat SSL - Renouvellement

Caddy gère automatiquement le renouvellement. Pour vérifier:

```bash
# Logs de renouvellement
sudo journalctl -u caddy | grep -i renew

# Date d'expiration du certificat
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

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
# 2. Vérifier que A et AAAA pointent vers l'IP du RPi
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

# Voir les ressources Docker
docker stats
```

### Base de données ne démarre pas

```bash
# Vérifier les logs
docker-compose logs database

# Vérifier l'espace disque
df -h

# Restaurer depuis backup
docker-compose exec -T database psql -U budget_user budget_db < backups/backup-latest.sql
```

---

## 📚 Fichiers Importants

| Fichier | Localisation | Objectif |
|---------|--------------|----------|
| .env | ~/apps/Project-budget/ | Configuration application |
| Caddyfile | /etc/caddy/ | Configuration reverse proxy |
| docker-compose.yml | ~/apps/Project-budget/ | Configuration Docker |
| Certificats SSL | /var/lib/caddy/ | Certificats Let's Encrypt |
| Logs Caddy | /var/log/caddy/ | Logs d'accès |
| Backups BD | ~/apps/Project-budget/backups/ | Sauvegardes PostgreSQL |

---

## 🎯 Commandes Essentielles

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

---

## ✨ Avantages de cette Configuration

✅ **HTTPS automatique** - Let's Encrypt via Caddy
✅ **Reverse proxy simple** - Caddy vs Nginx
✅ **DNS chez Infomaniak** - Facile à gérer
✅ **Données persistantes** - Docker volumes
✅ **Mises à jour sans perte** - Redémarrage transparent
✅ **Sauvegarde automatique** - Cron quotidien
✅ **Sécurisé** - Firewall + HTTPS + SSL/TLS
✅ **24/7 disponible** - Raspberry Pi économe en énergie
✅ **Accès interne et externe** - Réseau local + Internet

---

## 📱 Accès à l'Application

### Réseau Local (Wi-Fi/Ethernet RPi)

```
https://yourdomain.com
ou
http://192.168.1.100:3000 (sans Caddy)
```

### Réseau Externe (Internet)

```
https://yourdomain.com
(avec port forwarding configuré)
```

### Mobile

```
Ouvrir un navigateur → https://yourdomain.com
Ajouter un raccourci à l'écran d'accueil → PWA
```

---

## 🚀 Prochaines Étapes

1. ✅ Tester l'application: https://yourdomain.com
2. ✅ Créer un utilisateur avec passkey
3. ✅ Ajouter des comptes et transactions
4. ✅ Vérifier les sauvegardes automatiques
5. ✅ Moniter les performances

---

**Vous avez maintenant un serveur personnel sécurisé et professionnel! 🎉**

Pour plus d'informations sur Docker, consultez [DOCKER.md](./DOCKER.md)
