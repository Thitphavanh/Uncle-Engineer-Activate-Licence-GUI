# Production API Setup - Quick Start

## 🚀 วิธีเปลี่ยนจาก Time-based Token เป็น Static API Key

### Step 1: Generate API Key

```bash
python manage.py generate_api_key
```

คัดลอก API key ที่ได้

### Step 2: เพิ่ม API Key ใน .env

```bash
# แก้ไขไฟล์ .env
API_TOKEN=dcdefa98b7f0bed9a0cf5571db56c9ca82e68d0fdf04b708dc6025609f61d40d
```

### Step 3: เปลี่ยน Permission Class

แก้ไขไฟล์ `license/views.py`:

```python
# เปลี่ยนจาก
from .permissions import HasAPIToken

# เป็น
from .permissions import HasStaticAPIKey

# แล้วเปลี่ยนทุก ViewSet
class SoftwareNameViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [HasStaticAPIKey]  # เปลี่ยนตรงนี้

class LicenseViewSet(viewsets.ModelViewSet):
    permission_classes = [HasStaticAPIKey]  # เปลี่ยนตรงนี้

class ActivationLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [HasStaticAPIKey]  # เปลี่ยนตรงนี้
```

### Step 4: Restart Server

```bash
# Docker
docker-compose restart backend

# หรือ Local
python manage.py runserver
```

### Step 5: ทดสอบ

```bash
# ใช้ API key ที่ generate มา
curl -H "X-API-TOKEN: dcdefa98b7f0bed9a0cf5571db56c9ca82e68d0fdf04b708dc6025609f61d40d" \
     http://localhost:8000/api/software/
```

---

## ✅ ข้อดี Static API Key

| Feature | Time-based Token | Static API Key |
|---------|------------------|----------------|
| Token lifetime | 1 ชั่วโมง | ไม่มีวันหมดอายุ |
| Client complexity | สูง (ต้อง regenerate) | ต่ำ (ใช้ key เดียว) |
| Production ready | ❌ | ✅ |
| Integration | ยาก | ง่าย |

---

## 📝 Client Integration Examples

### Python Client

```python
import requests

API_KEY = "dcdefa98b7f0bed9a0cf5571db56c9ca82e68d0fdf04b708dc6025609f61d40d"
BASE_URL = "https://api.yourdomain.com"

# Validate License
def validate_license(software_name, machine_id, mac_address):
    headers = {"X-API-TOKEN": API_KEY}
    payload = {
        "software_name": software_name,
        "machine_id": machine_id,
        "mac_address": mac_address
    }

    response = requests.post(
        f"{BASE_URL}/api/licenses/validate/",
        json=payload,
        headers=headers
    )

    return response.json()

# Example usage
result = validate_license("Account1", "MACHINE-123", "00:1B:63:84:45:E6")
print(result)
```

### JavaScript Client

```javascript
const API_KEY = "dcdefa98b7f0bed9a0cf5571db56c9ca82e68d0fdf04b708dc6025609f61d40d";
const BASE_URL = "https://api.yourdomain.com";

async function validateLicense(softwareName, machineId, macAddress) {
  const response = await fetch(`${BASE_URL}/api/licenses/validate/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-TOKEN': API_KEY
    },
    body: JSON.stringify({
      software_name: softwareName,
      machine_id: machineId,
      mac_address: macAddress
    })
  });

  return await response.json();
}

// Example usage
validateLicense("Account1", "MACHINE-123", "00:1B:63:84:45:E6")
  .then(data => console.log(data));
```

---

## 🔒 Security Checklist

- [ ] Generate strong random API key (64+ characters)
- [ ] Store API key in `.env` file (not in code)
- [ ] Add `.env` to `.gitignore`
- [ ] Use HTTPS in production
- [ ] Set up rate limiting
- [ ] Monitor API usage logs
- [ ] Rotate keys every 6-12 months
- [ ] Consider IP whitelist for extra security

---

## 🆘 Troubleshooting

### ไม่สามารถเข้าถึง API ได้

```bash
# 1. ตรวจสอบว่า API_TOKEN ถูกตั้งค่า
echo $API_TOKEN

# 2. ตรวจสอบว่า server restart แล้ว
docker-compose ps

# 3. ทดสอบด้วย verbose mode
curl -v -H "X-API-TOKEN: your-key" http://localhost:8000/api/software/
```

### API key รั่วไหล - เปลี่ยนทันที!

```bash
# 1. Generate key ใหม่
python manage.py generate_api_key

# 2. อัพเดท .env
# API_TOKEN=new-key-here

# 3. Restart
docker-compose restart backend

# 4. แจ้งเตือน clients ให้อัพเดท key
```

---

## 📚 เอกสารเพิ่มเติม

ดู `PRODUCTION_API_SETUP.md` สำหรับรายละเอียดเพิ่มเติมเกี่ยวกับ:
- IP Whitelisting
- Multiple API Keys
- JWT Authentication
- OAuth2 Integration
- Advanced Security Features
