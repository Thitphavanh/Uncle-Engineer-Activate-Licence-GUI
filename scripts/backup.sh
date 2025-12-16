#!/bin/bash

# Database and Media Backup Script
# Creates backups of PostgreSQL database and media files

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"
MEDIA_BACKUP_FILE="$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "📦 Starting backup process..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Backup database
echo "💾 Backing up database..."
docker-compose exec -T db pg_dump -U ${DB_USER:-postgres} ${DB_NAME:-license_db} > $DB_BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Database backup created: $DB_BACKUP_FILE"
    gzip $DB_BACKUP_FILE
    echo "📦 Compressed: $DB_BACKUP_FILE.gz"
else
    echo "❌ Database backup failed!"
    exit 1
fi

# Backup media files
echo "📁 Backing up media files..."
tar -czf $MEDIA_BACKUP_FILE media/

if [ $? -eq 0 ]; then
    echo "✅ Media backup created: $MEDIA_BACKUP_FILE"
else
    echo "❌ Media backup failed!"
    exit 1
fi

# Remove backups older than 30 days
echo "🧹 Cleaning old backups (older than 30 days)..."
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "✅ Backup process completed successfully!"
echo "📊 Backup location: $BACKUP_DIR"
