#!/bin/bash

# ============================================
# Script de déploiement Docker
# Mise à jour sans perte de données
# ============================================

set -e  # Exit on error

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonctions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Vérifications préalables
check_requirements() {
    print_header "Vérification des prérequis"

    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé"
        exit 1
    fi
    print_success "Docker trouvé"

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé"
        exit 1
    fi
    print_success "Docker Compose trouvé"

    if [ ! -f ".env" ]; then
        print_error ".env n'existe pas"
        print_warning "Créer .env depuis .env.example ou .env.docker"
        exit 1
    fi
    print_success ".env trouvé"
}

# Mise à jour complète
deploy_all() {
    print_header "Déploiement Complet (Frontend + Backend)"

    print_warning "Récupération des dernières modifications..."
    git pull origin main

    print_warning "Construction des images..."
    docker-compose build

    print_warning "Redémarrage des services..."
    docker-compose up -d

    print_warning "Attente du démarrage..."
    sleep 5

    docker-compose ps

    print_success "Déploiement complet terminé!"
}

# Mise à jour frontend seulement
deploy_frontend() {
    print_header "Mise à Jour Frontend"

    git pull origin main
    docker-compose build frontend
    docker-compose up -d frontend

    sleep 3
    docker-compose ps frontend

    print_success "Frontend mis à jour!"
}

# Mise à jour backend seulement
deploy_backend() {
    print_header "Mise à Jour Backend"

    git pull origin main
    docker-compose build backend
    docker-compose up -d backend

    sleep 5
    docker-compose logs backend | tail -20

    print_success "Backend mis à jour!"
}

# Sauvegarde de la base de données
backup_database() {
    print_header "Sauvegarde Base de Données"

    mkdir -p backups
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="backups/backup_${TIMESTAMP}.sql"

    print_warning "Création de la sauvegarde: $BACKUP_FILE"
    docker-compose exec -T database pg_dump -U budget_user budget_db > "$BACKUP_FILE"

    print_success "Sauvegarde créée: $BACKUP_FILE"
    ls -lh "$BACKUP_FILE"
}

# Restauration de la base de données
restore_database() {
    if [ -z "$1" ]; then
        print_error "Spécifiez le fichier de sauvegarde"
        echo "Usage: $0 restore-db backups/backup_YYYYMMDD_HHMMSS.sql"
        exit 1
    fi

    if [ ! -f "$1" ]; then
        print_error "Fichier non trouvé: $1"
        exit 1
    fi

    print_header "Restauration Base de Données"
    print_warning "Restauration depuis: $1"
    print_warning "Cela remplacera les données actuelles!"

    read -p "Êtes-vous sûr? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Annulé"
        exit 0
    fi

    docker-compose exec -T database psql -U budget_user budget_db < "$1"
    print_success "Base de données restaurée!"
}

# Affichage des logs
show_logs() {
    SERVICE=$1
    if [ -z "$SERVICE" ]; then
        SERVICE="all"
    fi

    case $SERVICE in
        backend)
            docker-compose logs -f backend
            ;;
        frontend)
            docker-compose logs -f frontend
            ;;
        database)
            docker-compose logs -f database
            ;;
        all|*)
            docker-compose logs -f
            ;;
    esac
}

# Vérification de l'état
check_status() {
    print_header "État de l'Application"
    docker-compose ps

    echo ""
    print_header "Utilisation des Ressources"
    docker stats --no-stream
}

# Affichage de l'aide
show_help() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commandes disponibles:"
    echo "  deploy             Déploiement complet (Frontend + Backend)"
    echo "  deploy-frontend    Mise à jour Frontend uniquement"
    echo "  deploy-backend     Mise à jour Backend uniquement"
    echo "  backup             Sauvegarde de la base de données"
    echo "  restore <file>     Restauration de la base de données"
    echo "  logs [service]     Affichage des logs (backend|frontend|database|all)"
    echo "  status             État de l'application"
    echo "  start              Démarrer les conteneurs"
    echo "  stop               Arrêter les conteneurs"
    echo "  restart            Redémarrer les conteneurs"
    echo "  help               Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 deploy"
    echo "  $0 deploy-frontend"
    echo "  $0 backup"
    echo "  $0 restore backups/backup_20240211_120000.sql"
    echo "  $0 logs backend"
}

# Script principal
check_requirements

case "$1" in
    deploy)
        deploy_all
        ;;
    deploy-frontend)
        deploy_frontend
        ;;
    deploy-backend)
        deploy_backend
        ;;
    backup)
        backup_database
        ;;
    restore)
        restore_database "$2"
        ;;
    logs)
        show_logs "$2"
        ;;
    status)
        check_status
        ;;
    start)
        print_header "Démarrage des conteneurs"
        docker-compose up -d
        docker-compose ps
        ;;
    stop)
        print_header "Arrêt des conteneurs"
        docker-compose down
        print_success "Conteneurs arrêtés (données conservées)"
        ;;
    restart)
        print_header "Redémarrage des conteneurs"
        docker-compose restart
        sleep 3
        docker-compose ps
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Commande inconnue: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
