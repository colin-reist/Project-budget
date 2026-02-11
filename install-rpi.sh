#!/bin/bash

# ============================================
# Script d'installation automatisée
# Budget Tracker sur Raspberry Pi + Caddy
# ============================================

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Fonctions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Vérifications préalables
check_system() {
    print_header "Vérification du Système"

    # Vérifier si root
    if [ "$EUID" -ne 0 ]; then
        print_error "Ce script doit être exécuté en sudo"
        echo "Lancez: sudo bash install-rpi.sh"
        exit 1
    fi
    print_success "Privilèges sudo OK"

    # Vérifier la RAM
    RAM=$(free -h | awk '/^Mem:/ {print $2}')
    print_info "RAM disponible: $RAM"

    # Vérifier l'espace disque
    DISK=$(df -h / | awk 'NR==2 {print $4}')
    print_info "Espace disque libre: $DISK"

    # Vérifier la connexion Internet
    if ! ping -c 1 8.8.8.8 &> /dev/null; then
        print_error "Pas de connexion Internet"
        exit 1
    fi
    print_success "Connexion Internet OK"
}

# Installation des dépendances système
install_dependencies() {
    print_header "Installation des Dépendances Système"

    print_info "Mise à jour du système..."
    apt update && apt upgrade -y

    print_info "Installation des paquets essentiels..."
    apt install -y \
        curl \
        git \
        wget \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        ufw

    print_success "Dépendances installées"
}

# Installation de Docker
install_docker() {
    print_header "Installation de Docker"

    if command -v docker &> /dev/null; then
        print_warning "Docker est déjà installé"
        docker --version
        return
    fi

    print_info "Installation de Docker..."
    curl -sSL https://get.docker.com | sh

    print_info "Ajout de l'utilisateur au groupe docker..."
    usermod -aG docker $SUDO_USER

    print_success "Docker installé"
    docker --version
}

# Installation de Docker Compose
install_docker_compose() {
    print_header "Installation de Docker Compose"

    if command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose est déjà installé"
        docker-compose --version
        return
    fi

    print_info "Installation de Docker Compose..."
    apt install -y docker-compose

    print_success "Docker Compose installé"
    docker-compose --version
}

# Installation de Caddy
install_caddy() {
    print_header "Installation de Caddy"

    if command -v caddy &> /dev/null; then
        print_warning "Caddy est déjà installé"
        caddy --version
        return
    fi

    print_info "Installation de Caddy..."
    apt install -y caddy

    print_info "Activation du service Caddy..."
    systemctl enable caddy
    systemctl start caddy

    print_success "Caddy installé et activé"
    caddy --version
}

# Configuration du Firewall
setup_firewall() {
    print_header "Configuration du Firewall"

    if ufw status | grep -q "inactive"; then
        print_info "Activation du firewall..."

        ufw allow 22/tcp      # SSH
        ufw allow 80/tcp      # HTTP
        ufw allow 443/tcp     # HTTPS
        ufw --force enable

        print_success "Firewall activé"
    else
        print_warning "Firewall déjà activé"
    fi

    ufw status
}

# Clonage du projet
clone_project() {
    print_header "Clonage du Projet"

    INSTALL_DIR="/home/$SUDO_USER/apps"
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"

    if [ -d "Project-budget" ]; then
        print_warning "Le répertoire Project-budget existe déjà"
        print_info "Mise à jour du projet..."
        cd Project-budget
        git pull origin main
    else
        print_info "Clonage du projet..."
        git clone https://github.com/votre-username/Project-budget.git
        cd Project-budget
    fi

    # Changer la propriété
    chown -R $SUDO_USER:$SUDO_USER "$INSTALL_DIR/Project-budget"

    print_success "Projet cloné dans $INSTALL_DIR/Project-budget"
    echo "export PROJECT_DIR=\"$INSTALL_DIR/Project-budget\"" >> /home/$SUDO_USER/.bashrc
}

# Configuration de l'environnement
setup_environment() {
    print_header "Configuration de l'Environnement"

    PROJECT_DIR="/home/$SUDO_USER/apps/Project-budget"
    cd "$PROJECT_DIR"

    if [ ! -f ".env" ]; then
        print_info "Création du fichier .env..."
        cp .env.example .env

        # Génération de la clé secrète
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

        # Édition du fichier .env
        sed -i "s/CHANGE_ME_TO_A_RANDOM_SECRET_KEY/$SECRET_KEY/g" .env

        print_warning "ÉDITION REQUISE:"
        print_info "Veuillez éditer /home/$SUDO_USER/apps/Project-budget/.env"
        print_info "Remplacer:"
        print_info "  - yourdomain.com par votre domaine réel"
        print_info "  - POSTGRES_PASSWORD par un mot de passe fort"
        echo ""
        read -p "Appuyez sur Entrée quand vous avez édité le fichier .env..."
    else
        print_warning ".env existe déjà, pas de modification"
    fi

    chown $SUDO_USER:$SUDO_USER "$PROJECT_DIR/.env"
}

# Configuration de Caddy
setup_caddy() {
    print_header "Configuration de Caddy"

    PROJECT_DIR="/home/$SUDO_USER/apps/Project-budget"

    print_info "Copie du Caddyfile..."
    cp "$PROJECT_DIR/Caddyfile.example" /etc/caddy/Caddyfile.backup
    cp "$PROJECT_DIR/Caddyfile.example" /etc/caddy/Caddyfile

    print_warning "ÉDITION REQUISE:"
    print_info "Veuillez éditer /etc/caddy/Caddyfile"
    print_info "Remplacer 'yourdomain.com' par votre domaine réel"
    echo ""
    read -p "Appuyez sur Entrée quand vous avez édité le Caddyfile..."

    # Validation
    print_info "Validation du Caddyfile..."
    caddy validate --config /etc/caddy/Caddyfile

    if [ $? -eq 0 ]; then
        print_success "Caddyfile valide"
        systemctl restart caddy
        print_success "Caddy redémarré"
    else
        print_error "Erreur dans le Caddyfile"
        exit 1
    fi
}

# Lancement de l'application
start_application() {
    print_header "Lancement de l'Application"

    PROJECT_DIR="/home/$SUDO_USER/apps/Project-budget"
    cd "$PROJECT_DIR"

    print_info "Démarrage des conteneurs Docker..."
    sudo -u $SUDO_USER docker-compose up -d

    # Attendre un peu
    sleep 10

    print_info "Vérification des conteneurs..."
    sudo -u $SUDO_USER docker-compose ps

    print_success "Application lancée!"
}

# Configuration des sauvegardes
setup_backups() {
    print_header "Configuration des Sauvegardes Automatiques"

    BACKUP_SCRIPT="/home/$SUDO_USER/backup-db.sh"

    cat > "$BACKUP_SCRIPT" << 'BACKUP_EOF'
#!/bin/bash
cd /home/$SUDO_USER/apps/Project-budget
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T database pg_dump -U budget_user budget_db > backups/backup_${DATE}.sql
echo "Backup créé: backups/backup_${DATE}.sql"

# Garder seulement les 30 derniers backups
cd backups
ls -t | tail -n +31 | xargs -r rm
echo "Nettoyage des anciens backups effectué"
BACKUP_EOF

    chmod +x "$BACKUP_SCRIPT"
    chown $SUDO_USER:$SUDO_USER "$BACKUP_SCRIPT"

    # Ajouter au cron
    CRON_JOB="0 2 * * * /home/$SUDO_USER/backup-db.sh"
    (crontab -u $SUDO_USER -l 2>/dev/null | grep -v backup-db.sh; echo "$CRON_JOB") | crontab -u $SUDO_USER -

    print_success "Sauvegardes automatiques configurées (quotidien à 2h du matin)"
}

# Vérifications finales
final_checks() {
    print_header "Vérifications Finales"

    print_info "État des conteneurs..."
    docker-compose -f /home/$SUDO_USER/apps/Project-budget/docker-compose.yml ps

    print_info "Statut de Caddy..."
    systemctl status caddy

    print_info "Firewall..."
    ufw status

    print_info "IP du Raspberry Pi..."
    hostname -I
}

# Affichage des instructions finales
show_final_instructions() {
    print_header "Installation Terminée! 🎉"

    IP=$(hostname -I | awk '{print $1}')

    echo "
${GREEN}✓ Votre serveur Budget Tracker est prêt!${NC}

${YELLOW}PROCHAINES ÉTAPES:${NC}

1. ${BLUE}Configuration DNS chez Infomaniak:${NC}
   - Ajouter un enregistrement A pointant vers votre IP: $IP
   - Attendre la propagation DNS (5-15 minutes)
   - Test: ping yourdomain.com

2. ${BLUE}Port Forwarding (si accès externe):${NC}
   - Configurer le routeur pour rediriger:
     * Port 80 → 80 du RPi
     * Port 443 → 443 du RPi

3. ${BLUE}Accès à l'application:${NC}
   - Interne: http://$IP:3000
   - Externe: https://yourdomain.com (après DNS)

4. ${BLUE}Monitoring:${NC}
   - Logs: docker-compose logs -f backend
   - Caddy: sudo journalctl -u caddy -f
   - Ressources: docker stats

5. ${BLUE}Sauvegardes:${NC}
   - Automatiques: Chaque jour à 2h du matin
   - Manuel: /home/$SUDO_USER/backup-db.sh

${YELLOW}FICHIERS IMPORTANTS:${NC}
   .env: /home/$SUDO_USER/apps/Project-budget/.env
   Caddyfile: /etc/caddy/Caddyfile
   Logs Caddy: /var/log/caddy/access.log
   Backups: /home/$SUDO_USER/apps/Project-budget/backups/

${YELLOW}COMMANDES UTILES:${NC}
   Redémarrer l'app: cd /home/$SUDO_USER/apps/Project-budget && docker-compose restart
   Voir les logs: docker-compose logs -f backend
   Sauvegarder: /home/$SUDO_USER/backup-db.sh
   Vérifier Caddy: sudo systemctl status caddy

${GREEN}Documentation complète: RASPBERRY_PI_INFOMANIAK.md${NC}
"
}

# Main
main() {
    print_header "Installation Budget Tracker sur Raspberry Pi + Caddy"

    check_system
    install_dependencies
    install_docker
    install_docker_compose
    install_caddy
    setup_firewall
    clone_project
    setup_environment
    setup_caddy
    start_application
    setup_backups
    final_checks
    show_final_instructions

    print_success "Installation terminée avec succès! 🚀"
}

# Lancer l'installation
main
