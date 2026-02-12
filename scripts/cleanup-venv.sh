#!/bin/bash

# ============================================
# Script de Nettoyage des Environnements Virtuels Python
# ============================================
# Ce script supprime les environnements virtuels Python
# qui ne devraient pas être dans le repository Git
#
# Usage: ./scripts/cleanup-venv.sh

set -e

echo "🧹 Nettoyage des environnements virtuels Python"
echo "================================================"
echo ""

# Couleurs pour le terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier si on est à la racine du projet
if [ ! -f "docker-compose.yml" ]; then
    log_error "Ce script doit être exécuté depuis la racine du projet!"
    exit 1
fi

# Trouver tous les environnements virtuels
VENVS=()

# Chercher myvenv à la racine
if [ -d "myvenv" ]; then
    VENVS+=("myvenv")
fi

# Chercher myvenv dans backend
if [ -d "backend/myvenv" ]; then
    VENVS+=("backend/myvenv")
fi

# Chercher venv à la racine
if [ -d "venv" ]; then
    VENVS+=("venv")
fi

# Chercher venv dans backend
if [ -d "backend/venv" ]; then
    VENVS+=("backend/venv")
fi

# Vérifier si des environnements ont été trouvés
if [ ${#VENVS[@]} -eq 0 ]; then
    log_info "Aucun environnement virtuel trouvé. Projet déjà propre! ✅"
    exit 0
fi

# Afficher les environnements trouvés
echo "Environnements virtuels trouvés:"
for venv in "${VENVS[@]}"; do
    SIZE=$(du -sh "$venv" 2>/dev/null | cut -f1)
    echo "  - $venv ($SIZE)"
done
echo ""

# Calculer la taille totale
TOTAL_SIZE=$(du -shc "${VENVS[@]}" 2>/dev/null | tail -1 | cut -f1)
log_warn "Taille totale à supprimer: $TOTAL_SIZE"
echo ""

# Demander confirmation
read -p "Voulez-vous supprimer ces environnements virtuels? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Opération annulée."
    exit 0
fi

echo ""
log_info "Suppression en cours..."
echo ""

# Supprimer les environnements
for venv in "${VENVS[@]}"; do
    log_info "Suppression de $venv..."
    rm -rf "$venv"
    if [ $? -eq 0 ]; then
        echo "  ✅ Supprimé avec succès"
    else
        log_error "  ❌ Erreur lors de la suppression"
    fi
done

echo ""
log_info "Nettoyage terminé! 🎉"
echo ""
echo "ℹ️  Note: Les environnements virtuels sont maintenant dans .gitignore"
echo "   Utilisez Docker pour le développement ou créez un nouvel environnement"
echo "   virtuel avec: cd backend && python -m venv venv"
echo ""
