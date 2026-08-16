# 🚀 ToolZaara PDF Unlock & Repair Microservice

خدمة خلفية (Backend Microservice) فائقة السرعة والقوة مبنية بـ **Python + FastAPI** ومحركات **QPDF (`pikepdf`)** و **PyMuPDF (`fitz`)** لفك تشفير وتجاوز قيود ملفات الـ PDF وإصلاح بنيتها التالفة.

---

## 📁 محتويات المشروع:
- `main.py`: تطبيق الـ API الكامل مع دعم CORS والاستجابة بالبث المباشر (Streaming Response).
- `requirements.txt`: المكتبات المطلوبة.
- `Dockerfile`: لإنشاء حاوية Docker سريعة وخفيفة.
- `docker-compose.yml`: لتشغيل الخدمة بأمر واحد على أي سيرفر VPS.

---

## 🛠️ خيارات التشغيل والاستضافة:

### 1️⃣ التشغيل المحلي أو على سيرفر (Python مباشر):
```bash
pip install -r requirements.txt
python main.py
```
سيعمل الـ API على الرابط: `http://localhost:8000`

### 2️⃣ التشغيل عبر Docker (على أي استضافة VPS مثل Hostinger VPS):
```bash
docker compose up -d --build
```

### 3️⃣ الاستضافة المجانية على Render.com / Railway:
1. ارفع مجلد `pdf-unlock-service` إلى حسابك على GitHub.
2. ادخل إلى [Render.com](https://render.com) واضغط **New Web Service**.
3. اختر المستودع الخاص بك وسيقوم Render باكتشاف الـ Dockerfile وتشغيله فوراً مع رابط HTTPS مجاني (مثال: `https://toolzaara-pdf.onrender.com`).

---

## 🔗 نقاط النهاية (Endpoints):
- **GET `/`**: فحص حالة الخدمة (Health Check).
- **POST `/api/unlock-pdf`**:
  - `file`: ملف الـ PDF (Multipart/form-data).
  - `password`: كلمة السر (اختياري).
