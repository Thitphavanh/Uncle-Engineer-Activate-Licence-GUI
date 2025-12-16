#!/bin/bash

# Database Restore Script
# Restores PostgreSQL database from backup

set -e

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "❌ Error: Backup file not provided"
    echo "Usage: ./restore.sh path/to/backup.sql.gz"
    echo ""
    echo "Available backups:"
    ls -lh backups/*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1

# Check if file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "⚠️ WARNING: This will overwrite the current database!"
echo "📁 Backup file: $BACKUP_FILE"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Restore cancelled"
    exit 0
fi

# Decompress if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "📦 Decompressing backup..."
    gunzip -k $BACKUP_FILE
    BACKUP_FILE="${BACKUP_FILE%.gz}"
fi

# Stop web service
echo "🛑 Stopping web service..."
docker-compose stop web

# Restore database
echo "💾 Restoring database..."
docker-compose exec -T db psql -U ${DB_USER:-postgres} -d ${DB_NAME:-license_db} < $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Database restored successfully!"
else
    echo "❌ Database restore failed!"
    exit 1
fi

# Start web service
echo "▶️ Starting web service..."
docker-compose up -d web

echo "✅ Restore process completed successfully!"
