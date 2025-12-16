#!/bin/bash

# Deployment script for DigitalOcean
# This script automates the deployment process

set -e  # Exit on error

echo "🚀 Starting deployment process..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ Error: .env file not found!"
    echo "Please create .env file from .env.example"
    exit 1
fi

# Pull latest changes (if using git)
echo "📥 Pulling latest changes..."
git pull origin main || echo "⚠️ Git pull skipped or failed"

# Stop and remove old containers
echo "🛑 Stopping old containers..."
docker-compose down

# Remove old images (optional - uncomment if needed)
# docker-compose down --rmi all

# Build new images
echo "🔨 Building Docker images..."
docker-compose build --no-cache

# Start services
echo "▶️ Starting services..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "📊 Running database migrations..."
docker-compose exec -T web python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👤 Creating superuser (if not exists)..."
docker-compose exec -T web python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'changeme123')
    print('Superuser created successfully!')
else:
    print('Superuser already exists.')
EOF

# Show container status
echo "📋 Container status:"
docker-compose ps

# Show logs
echo "📝 Recent logs:"
docker-compose logs --tail=50 web

echo "✅ Deployment completed successfully!"
echo "🌐 Your application should be running now"
echo "📊 Check logs: docker-compose logs -f"
echo "🔍 Check status: docker-compose ps"
