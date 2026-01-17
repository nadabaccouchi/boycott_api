# Quick Reference - Reports API

## 🔑 Key Endpoints

### Auth (Public)
```bash
# Register
POST /auth/register
{"username": "user", "email": "user@example.com", "password": "pass123"}

# Login  
POST /auth/login
{"email": "user@example.com", "password": "pass123"}
```

### Reports (Authenticated)
```bash
# Create report
POST /reports
Authorization: Bearer TOKEN
{"product_id": 1, "message": "Issue here", "evidence_url": "link"}

# Get my reports
GET /reports/mine
Authorization: Bearer TOKEN

# Get all reports (ADMIN ONLY)
GET /reports
Authorization: Bearer ADMIN_TOKEN

# Update status (ADMIN ONLY)
PUT /reports/{id}
Authorization: Bearer ADMIN_TOKEN
{"status": "approved", "admin_note": "verified"}
```

---

## 🗄️ Models

### User
- id, username (unique), email (unique), password_hash, role, created_at

### Report
- id, user_id (FK), product_id (FK, nullable), barcode (nullable)
- message, evidence_url, status (pending/approved/rejected)
- admin_note, created_at, updated_at

---

## 🔐 Auth Functions

In `auth.py`:
- `create_access_token(user_id, role)` - Creates JWT
- `get_current_user()` - Returns User or 401
- `require_admin()` - Returns User or 403

---

## 📦 Dependencies Added

- PyJWT==2.10.1 (JWT handling)
- flask-smorest==0.42.0 (API framework)
- marshmallow==3.20.1 (Validation)
- Flask-Migrate==4.0.5 (Migrations)
- Werkzeug==2.3.7 (Password hashing)

---

## ✨ Features

✅ JWT authentication  
✅ Role-based authorization (user/admin)  
✅ Product-based or barcode-based reports  
✅ Admin review system  
✅ Status filtering  
✅ Full validation  
✅ Swagger docs included  

---

## 🚀 Setup (Already Done)

```bash
pip install -r requirements.txt
flask db upgrade  # ✅ Already ran
python app.py     # Start server
```

---

## 🧪 Quick Test

```bash
# 1. Register
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user1@test.com","password":"pass123"}'

# 2. Copy access_token from response

# 3. Create report
curl -X POST http://localhost:5000/reports \
  -H "Authorization: Bearer TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"message":"Test report","evidence_url":"https://example.com"}'

# 4. Get your reports
curl http://localhost:5000/reports/mine \
  -H "Authorization: Bearer TOKEN_HERE"
```

---

## 📄 Files Created

- `backend/models/user.py` - User model
- `backend/models/report.py` - Report model  
- `backend/auth.py` - JWT utilities
- `backend/resources/auth.py` - Login/register endpoints
- `backend/resources/reports.py` - Reports CRUD
- `backend/migrations/versions/add_auth_reports.py` - DB migration

---

## 📚 Full Docs

See [REPORTS_FEATURE_GUIDE.md](REPORTS_FEATURE_GUIDE.md) for complete documentation.
