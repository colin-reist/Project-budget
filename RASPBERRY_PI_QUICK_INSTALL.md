# 🚀 Installation Rapide: Raspberry Pi + Caddy + Infomaniak

Installation complète en **3 commandes**.

## ⚡ Installation Automatisée

### Sur le Raspberry Pi (SSH)

```bash
# 1. SSH sur le RPi
ssh pi@raspberrypi.local
# ou: ssh pi@192.168.1.100

# 2. Cloner et lancer l'installation
git clone https://github.com/votre-username/Project-budget.git
cd Project-budget
sudo bash install-rpi.sh

# 3. Suivre les instructions à l'écran
# L'installation va:
# - Installer Docker, Docker Compose, Caddy
# - Configurer le firewall
# - Cloner votre projet
# - Créer la configuration
# - Lancer l'application
```

## 🔧 Configuration Requise (2 étapes)

L'installation va s'arrêter et demander:

### 1️⃣ Éditer `.env`

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

### 2️⃣ Éditer `Caddyfile`

```bash
sudo nano /etc/caddy/Caddyfile
```

Remplacer **tous** les `yourdomain.com` par votre domaine réel.

Sauvegarder: `Ctrl+O`, `Entrée`, `Ctrl+X`

## 🌐 Configuration DNS chez Infomaniak

### Accès au Panneau

1. https://www.infomaniak.com → Connexion
2. Domaines → Gérer les domaines → Votre domaine
3. Onglet "DNS" ou "Enregistrements DNS"

### Trouver l'IP du RPi

```bash
# Sur le RPi
hostname -I
# Résultat: 192.168.1.100
```

### Ajouter les Enregistrements

| Type | Nom | Valeur | TTL |
|------|-----|--------|-----|
| **A** | @ | 192.168.1.100 | 3600 |
| **A** | www | 192.168.1.100 | 3600 |

*Si IPv6 disponible (optionnel):*

| Type | Nom | Valeur | TTL |
|------|-----|--------|-----|
| **AAAA** | @ | votre:ipv6:ici | 3600 |
| **AAAA** | www | votre:ipv6:ici | 3600 |

### Port Forwarding (Si accès externe)

Si vous accédez depuis l'extérieur:

1. Routeur → Configuration → Port Forwarding
2. Port 80 externe → Port 80 interne (RPi)
3. Port 443 externe → Port 443 interne (RPi)
4. Adresse IP: 192.168.1.100 (IP du RPi)

## ✅ Vérification

```bash
# SSH sur le RPi
ssh pi@raspberrypi.local

# État de l'application
docker-compose -f ~/apps/Project-budget/docker-compose.yml ps

# État de Caddy
sudo systemctl status caddy

# Logs
docker-compose -f ~/apps/Project-budget/docker-compose.yml logs -f backend
```

## 🌍 Accès à l'Application

### Réseau Local (Wi-Fi/Ethernet RPi)

```
http://192.168.1.100:3000
```

### Réseau Externe (Avec domaine)

```
https://yourdomain.com
```

## 📊 Commandes Essentielles

```bash
# Aller au projet
cd ~/apps/Project-budget

# État
docker-compose ps

# Logs
docker-compose logs -f backend

# Redémarrer
docker-compose restart

# Arrêter (données conservées)
docker-compose down

# Sauvegarder la BD
~/backup-db.sh

# Mettre à jour
git pull origin main && docker-compose build && docker-compose up -d

# Statut Caddy
sudo systemctl status caddy

# Logs Caddy
sudo journalctl -u caddy -f
```

## 🆘 Dépannage Rapide

### DNS ne fonctionne pas

```bash
# Vérifier dans Infomaniak
# - Enregistrement A ajouté?
# - IP correcte?
# - Attendre 5-15 minutes

# Test depuis RPi
nslookup yourdomain.com
ping yourdomain.com
```

### HTTPS ne fonctionne pas

```bash
# Vérifier les certificats
sudo ls -la /var/lib/caddy/

# Logs de Caddy
sudo journalctl -u caddy -f

# Valider la config
sudo caddy validate --config /etc/caddy/Caddyfile
```

### Application lente

```bash
# Espace disque
df -h

# Mémoire libre
free -h

# Ressources Docker
docker stats
```

## 📚 Documentation Complète

Pour plus de détails → **RASPBERRY_PI_INFOMANIAK.md**

## 🎯 Résumé

| Étape | Durée | Actions |
|-------|-------|---------|
| Installation automatisée | 10 min | `sudo bash install-rpi.sh` |
| Configuration .env | 2 min | Éditer le fichier |
| Configuration Caddyfile | 2 min | Éditer le fichier |
| Configuration DNS Infomaniak | 5 min | Ajouter enregistrements A |
| Propagation DNS | 5-15 min | Attendre |
| **Total** | **30 min** | Prêt à utiliser! |

## ✨ Après l'Installation

- ✅ Application accessible: https://yourdomain.com
- ✅ Certificat SSL automatique (Let's Encrypt)
- ✅ Sauvegardes quotidiennes à 2h du matin
- ✅ Logs et monitoring disponibles
- ✅ Mises à jour sans perte de données

**Vous avez maintenant un serveur personnel professionnel! 🚀**

Questions? Consultez **RASPBERRY_PI_INFOMANIAK.md** pour la documentation complète.
