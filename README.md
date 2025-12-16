# 🔐 Django License System - Backend

ระบบจัดการ License Keys สำหรับ Application โดยใช้ Django REST Framework

## 📋 Features

- ✅ สร้างและจัดการ License Keys
- ✅ ตรวจสอบความถูกต้องของ License
- ✅ จัดการ Machine IDs และการผูก License
- ✅ REST API สำหรับ Client Applications
- ✅ Admin Dashboard สำหรับจัดการ
- ✅ รองรับ PostgreSQL และ Redis
- ✅ พร้อม Deploy บน Docker

## 🛠️ Technology Stack

- **Backend Framework:** Django 5.2
- **API:** Django REST Framework
- **Database:** PostgreSQL (Production) / SQLite (Development)
- **Cache:** Redis
- **Web Server:** Gunicorn + Nginx
- **Containerization:** Docker & Docker Compose

## 📁 Project Structure

```
backend/
├── core/                      # Django project settings
│   ├── settings/             # Settings split by environment
│   │   ├── __init__.py
│   │   ├── base.py          # Base settings
│   │   ├── dev.py           # Development settings
│   │   └── prod.py          # Production settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── license/                   # License management app
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── admin.py
├── nginx/                     # Nginx configuration
│   ├── nginx.conf
│   └── conf.d/
│       └── default.conf
├── scripts/                   # Deployment scripts
│   ├── deploy.sh
│   ├── setup-ssl.sh
│   ├── backup.sh
│   └── restore.sh
├── static/                    # Static files
├── media/                     # Media files
├── logs/                      # Application logs
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Production compose
├── docker-compose.dev.yml     # Development compose
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore
├── manage.py
├── README.md
└── DEPLOYMENT.md             # Deployment guide

## 🚀 Quick Start

### Development Setup

1. **Clone Repository**
```bash
git clone <repository-url>
cd backend
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup Environment Variables**
```bash
cp .env.example .env
# Edit .env file with your settings
```

5. **Run Migrations**
```bash
python manage.py migrate
```

6. **Create Superuser**
```bash
python manage.py createsuperuser
```

7. **Run Development Server**
```bash
python manage.py runserver
```

8. **Access Application**
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

### Docker Development Setup

1. **Start Services**
```bash
docker compose -f docker-compose.dev.yml up -d
```

2. **Run Migrations**
```bash
docker compose -f docker-compose.dev.yml exec web python manage.py migrate
```

3. **Create Superuser**
```bash
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

4. **Access Application**
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

## 🌐 Production Deployment

สำหรับคำแนะนำการ Deploy แบบละเอียด กรุณาดูที่ [DEPLOYMENT.md](DEPLOYMENT.md)

### Quick Production Setup

1. **Setup Environment**
```bash
cp .env.example .env
nano .env  # Edit with production values
```

2. **Deploy**
```bash
./scripts/deploy.sh
```

3. **Setup SSL**
```bash
./scripts/setup-ssl.sh yourdomain.com
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout

### License Management
- `GET /api/licenses/` - List all licenses
- `POST /api/licenses/` - Create new license
- `GET /api/licenses/{id}/` - Get license details
- `PUT /api/licenses/{id}/` - Update license
- `DELETE /api/licenses/{id}/` - Delete license
- `POST /api/licenses/validate/` - Validate license

### License Validation Example

**Request:**
```bash
curl -X POST http://localhost:8000/api/licenses/validate/ \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "YOUR-LICENSE-KEY",
    "machine_id": "MACHINE-ID"
  }'
```

**Response:**
```json
{
  "valid": true,
  "license_key": "YOUR-LICENSE-KEY",
  "expires_at": "2025-12-31T23:59:59Z",
  "machine_id": "MACHINE-ID"
}
```

## 🔧 Management Commands

### Database
```bash
# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Reset database
python manage.py flush
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic

# Clear cache
python manage.py clearcache
```

### Users
```bash
# Create superuser
python manage.py createsuperuser

# Change user password
python manage.py changepassword <username>
```

## 🔒 Security Configuration

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use strong database passwords
- [ ] Setup SSL/TLS certificates
- [ ] Enable firewall (UFW)
- [ ] Regular backups
- [ ] Monitor logs
- [ ] Keep dependencies updated

## 📊 Monitoring & Logs

### View Logs
```bash
# Application logs
tail -f logs/django.log

# Docker logs
docker-compose logs -f web

# Nginx logs
docker-compose logs -f nginx
```

### Check Status
```bash
# Container status
docker-compose ps

# Resource usage
docker stats
```

## 🔄 Backup & Restore

### Backup
```bash
./scripts/backup.sh
```

### Restore
```bash
./scripts/restore.sh backups/db_backup_YYYYMMDD_HHMMSS.sql.gz
```

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📦 Dependencies

Key dependencies (see `requirements.txt` for full list):

- Django 5.2.9
- Django REST Framework 3.14+
- psycopg2-binary 2.9+ (PostgreSQL)
- django-redis 5.4+ (Redis cache)
- gunicorn 21.2+ (WSGI server)
- whitenoise 6.6+ (Static files)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

## 👥 Support

For support and questions:
- Email: support@yourdomain.com
- GitHub Issues: https://github.com/yourusername/your-repo/issues

## 🎉 Acknowledgments

- Django Team
- Django REST Framework Team
- DigitalOcean Community

---

Made with ❤️ by Your Team
