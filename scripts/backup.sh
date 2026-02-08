#!/bin/bash

# Configuration
BACKUP_DIR="$(dirname "$0")/../backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Créer le répertoire de backup s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Backup de la base de données
echo "Creating database backup..."
docker-compose exec -T database pg_dump -U budget_user budget_db | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

if [ $? -eq 0 ]; then
    echo "Database backup completed: db_backup_$DATE.sql.gz"
else
    echo "Error: Database backup failed!"
    exit 1
fi

# Backup des fichiers media (si utilisés)
if [ -d "../backend/media" ] && [ "$(ls -A ../backend/media)" ]; then
    echo "Creating media backup..."
    tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" -C ../backend media/
    
    if [ $? -eq 0 ]; then
        echo "Media backup completed: media_backup_$DATE.tar.gz"
    else
        echo "Warning: Media backup failed!"
    fi
fi

# Supprimer les backups de plus de X jours
echo "Cleaning old backups..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup process completed: $DATE"
echo "Backup location: $BACKUP_DIR"
