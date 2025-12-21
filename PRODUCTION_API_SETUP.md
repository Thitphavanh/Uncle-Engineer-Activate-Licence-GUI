# Production API Authentication Setup

## ภาพรวม

ระบบมี 2 วิธีในการ authenticate API:

### 1. Static API Key (แนะนำสำหรับ Production)
- API key คงที่ที่ไม่เปลี่ยนแปลง
- เหมาะกับ server-to-server communication
- ง่ายต่อการ integrate กับ client applications

### 2. Time-based Token (สำหรับ Development/Testing)
- Token ที่ generate ใหม่ทุกชั่วโมง
- เหมาะสำหรับ development และ testing

---

## วิธีที่ 1: Static API Key (Production)

### ขั้นตอนการตั้งค่า

#### 1. Generate API Key ที่แข็งแรง

```bash
# Linux/Mac
openssl rand -hex 32

# หรือใช้ Python
python -c "import secrets; print(secrets.token_hex(32))"
```

ตัวอย่างผลลัพธ์:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

#### 2. ตั้งค่าใน `.env`

```bash
# Production .env
API_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

#### 3. อัพเดท Views ให้ใช้ HasStaticAPIKey

แก้ไขไฟล์ `license/views.py`:

```python
from .permissions import HasStaticAPIKey  # เปลี่ยนจาก HasAPIToken

class SoftwareNameViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SoftwareName.objects.filter(is_active=True)
    serializer_class = SoftwareNameSerializer
    permission_classes = [HasStaticAPIKey]  # เปลี่ยนเป็น HasStaticAPIKey

class LicenseViewSet(viewsets.ModelViewSet):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    permission_classes = [HasStaticAPIKey]  # เปลี่ยนเป็น HasStaticAPIKey
    # ... rest of the code
```

#### 4. Restart Server

```bash
docker-compose restart backend
# หรือ
python manage.py runserver
```

### การใช้งาน Client

#### Python Client

```python
import requests

API_KEY = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"
BASE_URL = "https://api.yourdomain.com"

# วิธีที่ 1: ใช้ Header (แนะนำ)
headers = {"X-API-TOKEN": API_KEY}
response = requests.get(f"{BASE_URL}/api/software/", headers=headers)

# วิธีที่ 2: ใช้ Query Parameter
response = requests.get(f"{BASE_URL}/api/software/?token={API_KEY}")

print(response.json())
```

#### JavaScript/Node.js Client

```javascript
const API_KEY = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2";
const BASE_URL = "https://api.yourdomain.com";

// วิธีที่ 1: ใช้ Header (แนะนำ)
fetch(`${BASE_URL}/api/software/`, {
  headers: {
    'X-API-TOKEN': API_KEY
  }
})
  .then(response => response.json())
  .then(data => console.log(data));

// วิธีที่ 2: ใช้ Query Parameter
fetch(`${BASE_URL}/api/software/?token=${API_KEY}`)
  .then(response => response.json())
  .then(data => console.log(data));
```

#### cURL

```bash
# วิธีที่ 1: Header
curl -H "X-API-TOKEN: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2" \
     https://api.yourdomain.com/api/software/

# วิธีที่ 2: Query Parameter
curl "https://api.yourdomain.com/api/software/?token=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"
```

---

## วิธีที่ 2: Time-based Token (Development/Testing)

### การใช้งาน

ใช้ `HasAPIToken` permission class (ค่าเริ่มต้น):

```python
from .permissions import HasAPIToken

class SoftwareNameViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [HasAPIToken]
```

### Generate Token

```bash
python manage.py generate_token
```

Token จะหมดอายุทุกชั่วโมง

---

## Security Best Practices

### 1. เก็บ API Key อย่างปลอดภัย

❌ **ไม่ควรทำ:**
```python
# Hard-code ใน source code
API_KEY = "a1b2c3d4..."
```

✅ **ควรทำ:**
```python
# ใช้ environment variables
import os
API_KEY = os.getenv('API_TOKEN')
```

### 2. ใช้ HTTPS เสมอ

```python
# Production
BASE_URL = "https://api.yourdomain.com"  # ✅

# Development only
BASE_URL = "http://localhost:8000"  # ❌ ห้ามใช้ใน production
```

### 3. Rotate API Keys เป็นระยะ

- เปลี่ยน API key ทุก 6-12 เดือน
- เปลี่ยนทันทีถ้า key รั่วไหล
- แจ้งเตือน clients ล่วงหน้าก่อนเปลี่ยน

### 4. Monitor API Usage

- ตรวจสอบ logs เป็นประจำ
- ติดตั้ง rate limiting
- Alert เมื่อมีการใช้งานผิดปกติ

### 5. IP Whitelist (Optional)

เพิ่มการตรวจสอบ IP address ใน permission class:

```python
class HasStaticAPIKey(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get('X-API-TOKEN') or request.query_params.get('token')

        if not api_key or api_key != settings.API_TOKEN:
            return False

        # IP Whitelist
        allowed_ips = getattr(settings, 'ALLOWED_API_IPS', [])
        if allowed_ips:
            client_ip = self.get_client_ip(request)
            if client_ip not in allowed_ips:
                return False

        return True

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

---

## Troubleshooting

### ❌ Error: "ไม่พบข้อมูลการเข้าสู่ระบบ"

**สาเหตุ:**
- ไม่ได้ส่ง API key
- API key ผิด

**วิธีแก้:**
```bash
# ตรวจสอบว่า API_TOKEN ถูกตั้งค่าใน .env หรือไม่
echo $API_TOKEN

# ตรวจสอบว่า client ส่ง key ถูกต้อง
curl -v -H "X-API-TOKEN: your-key" http://localhost:8000/api/software/
```

### ❌ Error: "API_TOKEN is not set"

**วิธีแก้:**
```bash
# เพิ่มใน .env
echo "API_TOKEN=your-generated-key" >> .env

# Restart server
docker-compose restart backend
```

---

## Migration Plan

### จาก Time-based Token → Static API Key

1. **Deploy แบบ backward compatible:**
   ```python
   # รองรับทั้ง 2 วิธี
   permission_classes = [HasAPIToken | HasStaticAPIKey]
   ```

2. **แจ้งเตือน clients ให้เปลี่ยนมาใช้ static key**

3. **หลังจาก clients เปลี่ยนเสร็จทั้งหมด:**
   ```python
   permission_classes = [HasStaticAPIKey]
   ```

---

## คำแนะนำเพิ่มเติม

สำหรับความปลอดภัยสูงสุด พิจารณาใช้:
- **Multiple API Keys** - แยก key ตาม client หรือ environment
- **JWT Tokens** - สำหรับ user-specific authentication
- **OAuth2** - สำหรับ third-party integrations
- **Rate Limiting** - จำกัดจำนวน requests ต่อ API key

ดู Django REST Framework documentation สำหรับรายละเอียดเพิ่มเติม:
https://www.django-rest-framework.org/api-guide/authentication/
