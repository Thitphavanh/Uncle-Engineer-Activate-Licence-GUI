#!/bin/bash

# SSL Setup Script using Let's Encrypt (Certbot)
# Run this script after deploying to DigitalOcean

set -e

echo "🔐 Setting up SSL certificates with Let's Encrypt..."

# Check if domain is provided
if [ -z "$1" ]; then
    echo "❌ Error: Domain name not provided"
    echo "Usage: ./setup-ssl.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-"admin@$DOMAIN"}

echo "📧 Domain: $DOMAIN"
echo "📧 Email: $EMAIL"

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing Certbot..."
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
fi

# Stop nginx temporarily
echo "🛑 Stopping nginx..."
docker-compose stop nginx

# Obtain certificate
echo "📜 Obtaining SSL certificate..."
sudo certbot certonly --standalone \
    --preferred-challenges http \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

# Copy certificates to nginx ssl directory
echo "📋 Copying certificates..."
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/
sudo chmod 644 nginx/ssl/fullchain.pem
sudo chmod 600 nginx/ssl/privkey.pem

# Update nginx configuration with correct domain
echo "⚙️ Updating nginx configuration..."
sed -i "s/yourdomain.com/$DOMAIN/g" nginx/conf.d/licenses.conf

# Start nginx
echo "▶️ Starting nginx..."
docker-compose up -d nginx

# Setup auto-renewal
echo "🔄 Setting up auto-renewal..."
sudo certbot renew --dry-run

echo "✅ SSL certificates installed successfully!"
echo "🌐 Your site should now be accessible via HTTPS"
echo "🔄 Certificates will auto-renew via certbot"
