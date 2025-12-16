# 🚀 Quick Start Guide - Deploy ใน 5 นาที

คู่มือสั้นๆ สำหรับการ Deploy Django License System บน DigitalOcean อย่างรวดเร็ว

## 📋 Prerequisites

- ✅ DigitalOcean Account
- ✅ Domain Name (Optional แต่แนะนำ)
- ✅ SSH Key หรือ Password

---

## 🔥 Step 1: สร้าง Droplet (2 นาที)

1. Login เข้า DigitalOcean
2. Create Droplet:
   - **OS:** Ubuntu 22.04 LTS
   - **Plan:** Basic - 2GB RAM / 1 CPU ($12/month)
   - **Datacenter:** Singapore (สำหรับ Thailand)
   - **Add SSH Key** หรือ set Password

3. รอ Droplet พร้อมใช้งาน (~1 นาที)
4. จดบันทึก **IP Address**

---

## 🛠️ Step 2: Setup Server (2 นาที)

SSH เข้า Server:
```bash
ssh root@YOUR_DROPLET_IP
```

Run คำสั่งเดียว ติดตั้งทุกอย่าง:
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Git
apt install git -y

# Setup Firewall
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
```

---

## 📦 Step 3: Deploy Application (1 นาที)

```bash
# Clone หรือ Upload project
cd /opt
git clone YOUR_REPO_URL license-system
# หรือ scp -r /path/to/backend root@YOUR_IP:/opt/license-system/

# เข้าไปที่ backend directory
cd license-system/backend

# สร้าง .env file
cp .env.example .env
nano .env
```

**แก้ไข .env (ค่าสำคัญ):**
```env
SECRET_KEY=<สร้างใหม่ด้วย: python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
ALLOWED_HOSTS=YOUR_DOMAIN,www.YOUR_DOMAIN,YOUR_DROPLET_IP
DB_PASSWORD=<รหัสผ่าน-แข็งแรง>
```

**Deploy:**
```bash
# ทำให้ scripts executable
chmod +x scripts/*.sh

# Deploy!
./scripts/deploy.sh
```

✅ เสร็จแล้ว! Application ทำงานแล้วที่ `http://YOUR_DROPLET_IP`

---

## 🔐 Step 4: Setup SSL (ถ้ามี Domain)

```bash
# Run SSL setup script
./scripts/setup-ssl.sh yourdomain.com your-email@gmail.com
```

✅ เสร็จแล้ว! Application ทำงานที่ `https://yourdomain.com`

---

## 🎯 เข้าใช้งาน

### Admin Panel
- URL: `https://yourdomain.com/admin/`
- Username: `admin` (default from deploy script)
- Password: `changeme123` (เปลี่ยนทันที!)

### API
- Base URL: `https://yourdomain.com/api/`
- Health Check: `https://yourdomain.com/health/`

---

## 🔧 คำสั่งที่ใช้บ่อย

```bash
# ดู logs
docker-compose logs -f web

# ดู status
docker-compose ps

# Restart
docker-compose restart

# Stop
docker-compose down

# Start
docker-compose up -d

# Backup database
./scripts/backup.sh

# เปลี่ยน admin password
docker-compose exec web python manage.py changepassword admin
```

---

## ⚠️ ก่อนเข้า Production

1. ✅ เปลี่ยน `SECRET_KEY` เป็นค่าใหม่
2. ✅ เปลี่ยน admin password เป็นรหัสที่แข็งแรง
3. ✅ ตั้งค่า `ALLOWED_HOSTS` ให้ถูกต้อง
4. ✅ Setup SSL Certificate
5. ✅ ตั้งค่า automatic backup (cron job)
6. ✅ Monitor logs เป็นประจำ

### Setup Automatic Backup

```bash
# Edit crontab
crontab -e

# เพิ่มบรรทัดนี้ (backup ทุกวัน 2:00 AM)
0 2 * * * cd /opt/license-system/backend && ./scripts/backup.sh
```

---

## 🆘 ปัญหาที่พบบ่อย

### Container ไม่ Start
```bash
docker-compose logs
docker-compose down && docker-compose up -d
```

### Database Connection Error
```bash
# ตรวจสอบ .env
cat .env

# Restart database
docker-compose restart db
```

### Permission Error
```bash
chown -R 1000:1000 media/ logs/ staticfiles/
docker-compose restart
```

---

## 📚 อ่านเพิ่มเติม

- **Full Documentation:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **README:** [README.md](README.md)
- **API Docs:** Available at `/api/` after deployment

---

## 🎉 เสร็จแล้ว!

Application ของคุณพร้อมใช้งานแล้ว!

**Next Steps:**
1. เปลี่ยน admin password
2. Create licenses ผ่าน Admin Panel
3. Test API endpoints
4. Setup monitoring และ backup

**Need Help?**
- Email: support@yourdomain.com
- Docs: [DEPLOYMENT.md](DEPLOYMENT.md)

---

Made with ❤️ | Happy Deploying! 🚀
