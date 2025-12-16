# 🚀 คู่มือการ Deploy Django License System บน DigitalOcean

คู่มือนี้จะแนะนำการ Deploy Django Backend ขึ้น DigitalOcean โดยใช้ Docker, PostgreSQL, Redis และ Nginx

## 📋 สารบัญ

1. [ความต้องการระบบ](#ความต้องการระบบ)
2. [การเตรียม Droplet บน DigitalOcean](#การเตรียม-droplet-บน-digitalocean)
3. [การติดตั้ง Dependencies](#การติดตั้ง-dependencies)
4. [การตั้งค่า Project](#การตั้งค่า-project)
5. [การ Deploy](#การ-deploy)
6. [การตั้งค่า SSL Certificate](#การตั้งค่า-ssl-certificate)
7. [การจัดการและ Maintenance](#การจัดการและ-maintenance)
8. [Troubleshooting](#troubleshooting)

---

## ความต้องการระบบ

### ขั้นต่ำ (Minimum Requirements)
- **RAM:** 2GB
- **CPU:** 1 vCPU
- **Storage:** 25GB SSD
- **OS:** Ubuntu 22.04 LTS

### แนะนำ (Recommended)
- **RAM:** 4GB+
- **CPU:** 2 vCPUs
- **Storage:** 50GB+ SSD
- **OS:** Ubuntu 22.04 LTS

---

## การเตรียม Droplet บน DigitalOcean

### 1. สร้าง Droplet ใหม่

1. เข้าสู่ระบบ DigitalOcean Console
2. คลิก "Create" → "Droplets"
3. เลือก Configuration:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic (2GB RAM / 1 vCPU) หรือสูงกว่า
   - **Datacenter:** เลือกตามความเหมาะสม (แนะนำ Singapore สำหรับประเทศไทย)
   - **Authentication:** SSH Key (แนะนำ) หรือ Password
   - **Hostname:** license-server (หรือชื่อที่ต้องการ)

4. คลิก "Create Droplet"

### 2. Point Domain ไปที่ Droplet (ถ้ามี)

1. ไปที่ DNS Management ของ Domain Provider
2. เพิ่ม A Record:
   ```
   Type: A
   Name: @
   Value: [Your Droplet IP]
   TTL: 3600
   ```
3. เพิ่ม A Record สำหรับ www:
   ```
   Type: A
   Name: www
   Value: [Your Droplet IP]
   TTL: 3600
   ```

---

## การติดตั้ง Dependencies

### 1. SSH เข้าสู่ Droplet

```bash
ssh root@your_droplet_ip
```

### 2. Update System

```bash
apt update && apt upgrade -y
```

### 3. ติดตั้ง Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Start and enable Docker
systemctl start docker
systemctl enable docker

# Verify installation
docker --version
```

### 4. ติดตั้ง Docker Compose

```bash
# Download Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### 5. ติดตั้ง Git

```bash
apt install git -y
git --version
```

### 6. ตั้งค่า Firewall (UFW)

```bash
# Enable UFW
ufw --force enable

# Allow SSH (สำคัญมาก!)
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Check status
ufw status
```

---

## การตั้งค่า Project

### 1. Clone Project จาก Git (ถ้ามี)

```bash
cd /opt
git clone https://github.com/yourusername/your-repo.git license-system
cd license-system/backend
```

หรือ Upload Project ผ่าน SCP:

```bash
# จาก Local Machine
scp -r /path/to/backend root@your_droplet_ip:/opt/license-system/
```

### 2. สร้างไฟล์ .env

```bash
cd /opt/license-system/backend
cp .env.example .env
nano .env
```

แก้ไขค่าต่างๆ ในไฟล์ .env:

```env
# Django Settings
DJANGO_ENV=production
SECRET_KEY=your-super-secret-key-here-generate-new-one
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your_droplet_ip

# Database
DB_NAME=license_db
DB_USER=postgres
DB_PASSWORD=your-strong-password-here
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/1

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security
SECURE_SSL_REDIRECT=True

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# Admin URL
ADMIN_URL=admin/
```

**สำคัญ:** สร้าง SECRET_KEY ใหม่:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. แก้ไข Nginx Configuration (ถ้าใช้ Domain)

```bash
nano nginx/conf.d/default.conf
```

แก้ไข `yourdomain.com` เป็น Domain จริงของคุณ

---

## การ Deploy

### 1. Deploy แบบ Manual

```bash
cd /opt/license-system/backend

# Build และ Start services
docker-compose up -d --build

# รอให้ services พร้อม
sleep 20

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### 2. Deploy แบบใช้ Script (แนะนำ)

```bash
cd /opt/license-system/backend

# ทำให้ script executable (ถ้ายังไม่ได้ทำ)
chmod +x scripts/*.sh

# Run deployment script
./scripts/deploy.sh
```

### 3. ตรวจสอบ Status

```bash
# ดู containers ที่กำลังทำงาน
docker-compose ps

# ดู logs
docker-compose logs -f web

# ตรวจสอบ health
curl http://localhost/health/
```

---

## การตั้งค่า SSL Certificate

### วิธีที่ 1: ใช้ Let's Encrypt (แนะนำ)

```bash
cd /opt/license-system/backend

# Run SSL setup script
./scripts/setup-ssl.sh yourdomain.com admin@yourdomain.com
```

### วิธีที่ 2: Setup Manual

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Stop nginx temporarily
docker-compose stop nginx

# Obtain certificate
certbot certonly --standalone \
  --preferred-challenges http \
  --email admin@yourdomain.com \
  --agree-tos \
  -d yourdomain.com \
  -d www.yourdomain.com

# Copy certificates
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Update nginx config
sed -i 's/yourdomain.com/your-actual-domain.com/g' nginx/conf.d/default.conf

# Restart nginx
docker-compose up -d nginx
```

### Auto-renewal Certificate

```bash
# Test renewal
certbot renew --dry-run

# Setup cron job for auto-renewal
crontab -e

# เพิ่มบรรทัดนี้:
0 0 1 * * certbot renew --quiet && docker-compose restart nginx
```

---

## การจัดการและ Maintenance

### การดู Logs

```bash
# ดู logs ทั้งหมด
docker-compose logs

# ดู logs แบบ real-time
docker-compose logs -f

# ดู logs เฉพาะ service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db
```

### การ Restart Services

```bash
# Restart ทั้งหมด
docker-compose restart

# Restart เฉพาะ service
docker-compose restart web
docker-compose restart nginx
```

### การ Backup Database

```bash
cd /opt/license-system/backend

# Backup แบบ manual
./scripts/backup.sh

# Setup automatic backup (cron job)
crontab -e

# เพิ่มบรรทัดนี้ (backup ทุกวัน เวลา 2:00 AM):
0 2 * * * cd /opt/license-system/backend && ./scripts/backup.sh
```

### การ Restore Database

```bash
cd /opt/license-system/backend

# ดู backups ที่มี
ls -lh backups/

# Restore จาก backup
./scripts/restore.sh backups/db_backup_20240101_020000.sql.gz
```

### การ Update Application

```bash
cd /opt/license-system/backend

# Pull latest code (ถ้าใช้ Git)
git pull origin main

# Rebuild และ restart
docker-compose down
docker-compose up -d --build

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### การตรวจสอบ Resource Usage

```bash
# ดู resource usage ของ containers
docker stats

# ดู disk usage
df -h

# ดู memory usage
free -h
```

---

## Troubleshooting

### 1. Container ไม่ Start

```bash
# ดู logs เพื่อหา error
docker-compose logs

# ตรวจสอบ .env file
cat .env

# Restart containers
docker-compose down
docker-compose up -d
```

### 2. Database Connection Error

```bash
# ตรวจสอบว่า database container ทำงานอยู่
docker-compose ps db

# ดู database logs
docker-compose logs db

# ทดสอบ connection
docker-compose exec web python manage.py dbshell
```

### 3. Static Files ไม่แสดง

```bash
# Collect static files ใหม่
docker-compose exec web python manage.py collectstatic --noinput

# ตรวจสอบ permissions
ls -la staticfiles/

# Restart nginx
docker-compose restart nginx
```

### 4. Permission Denied Errors

```bash
# Fix permissions
chown -R 1000:1000 media/ logs/ staticfiles/

# Restart services
docker-compose restart
```

### 5. Out of Memory

```bash
# เพิ่ม swap space
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 6. SSL Certificate Issues

```bash
# ตรวจสอบ certificate files
ls -la nginx/ssl/

# Test nginx configuration
docker-compose exec nginx nginx -t

# Restart nginx
docker-compose restart nginx
```

---

## 🔒 Security Best Practices

1. **เปลี่ยน Secret Key:** อย่าใช้ default secret key
2. **Strong Passwords:** ใช้รหัสผ่านที่แข็งแรงสำหรับ database และ admin
3. **Firewall:** เปิดเฉพาะ ports ที่จำเป็น
4. **Regular Updates:** อัพเดท system และ packages เป็นประจำ
5. **Backups:** ทำ backup database เป็นประจำ
6. **SSL/TLS:** ใช้ HTTPS เสมอใน production
7. **Monitor Logs:** ตรวจสอบ logs เป็นประจำ
8. **Limit Access:** จำกัดการเข้าถึง SSH (ใช้ SSH key แทน password)

---

## 📞 Support

หากมีปัญหาหรือข้อสงสัย สามารถติดต่อได้ที่:

- **Email:** support@yourdomain.com
- **GitHub Issues:** https://github.com/yourusername/your-repo/issues

---

## 📝 License

Copyright © 2024 Your Company Name. All rights reserved.
