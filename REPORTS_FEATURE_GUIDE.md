# Reports Feature - Authentication & Authorization Guide

## Overview
This implementation adds a **Reports** feature with JWT-based authentication and role-based authorization to your Flask API.

---

## Features Implemented

### 1. Authentication System
- **JWT Tokens**: Stateless token-based authentication
- **User Registration** (`POST /auth/register`)
- **User Login** (`POST /auth/login`)
- **Password Hashing**: Using Werkzeug's secure password hashing

### 2. Role-Based Access Control
- **Roles**: `"user"` (default) or `"admin"`
- **Dependencies**:
  - `get_current_user()`: Extracts and validates JWT token, returns User object
  - `require_admin()`: Ensures user has admin role, else returns 403

### 3. Reports Model
The `Report` table includes:
- `id` (PK)
- `user_id` (FK to users)
- `product_id` (FK to products, nullable)
- `barcode` (string, optional, max 14 chars)
- `message` (text, required)
- `evidence_url` (string, optional)
- `status` (enum: pending/approved/rejected, default: pending)
- `admin_note` (text, optional)
- `created_at` (timestamp)
- `updated_at` (timestamp)

---

## API Endpoints

### Authentication

#### Register User
```bash
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response** (201):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user",
    "created_at": "2025-01-17T10:00:00"
  }
}
```

#### Login User
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response** (200): Same as register response

---

### Reports

#### Create Report (Auth Required)
```bash
POST /reports
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "product_id": 55,
  "message": "Product contains controversial ingredient X",
  "evidence_url": "https://example.com/evidence.pdf"
}
```

**OR** using barcode:
```json
{
  "barcode": "6194002400707",
  "message": "Unethical labor practices reported",
  "evidence_url": "https://example.com/evidence.pdf"
}
```

**Response** (201):
```json
{
  "id": 1,
  "user_id": 1,
  "product_id": 55,
  "barcode": null,
  "message": "Product contains controversial ingredient X",
  "evidence_url": "https://example.com/evidence.pdf",
  "status": "pending",
  "admin_note": null,
  "created_at": "2025-01-17T10:00:00",
  "updated_at": "2025-01-17T10:00:00"
}
```

---

#### Get My Reports (Auth Required)
```bash
GET /reports/mine
Authorization: Bearer <your_jwt_token>
```

**Response** (200):
```json
[
  {
    "id": 1,
    "user_id": 1,
    "product_id": 55,
    "barcode": null,
    "message": "Product contains controversial ingredient X",
    "evidence_url": "https://example.com/evidence.pdf",
    "status": "pending",
    "admin_note": null,
    "created_at": "2025-01-17T10:00:00",
    "updated_at": "2025-01-17T10:00:00"
  }
]
```

---

#### Get All Reports (Admin Only)
```bash
GET /reports
Authorization: Bearer <admin_jwt_token>
```

**Optional query parameter for filtering**:
```bash
GET /reports?status=pending
GET /reports?status=approved
GET /reports?status=rejected
```

**Response** (200): Array of all reports

---

#### Get Single Report (Admin Only)
```bash
GET /reports/{id}
Authorization: Bearer <admin_jwt_token>
```

**Response** (200): Single report object

---

#### Update Report Status (Admin Only)
```bash
PUT /reports/{id}
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "status": "approved",
  "admin_note": "Verified against official sources"
}
```

**Response** (200): Updated report object

---

## HTTP Status Codes & Error Handling

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success (GET, PUT) | Report updated |
| 201 | Created (POST) | Report created |
| 400 | Bad Request | Missing required field |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Non-admin trying to access admin endpoint |
| 404 | Not Found | Report/Product not found |
| 409 | Conflict | Email/username already exists |

---

## Security Implementation

### 1. Token-Based Authentication
- **Header**: `Authorization: Bearer <token>`
- **Token Format**: JWT (Header.Payload.Signature)
- **Secret Key**: Uses `Config.SECRET_KEY` (set in config.py)
- **Expiration**: 24 hours by default

### 2. Password Security
- Hashed using Werkzeug's PBKDF2 algorithm
- Never stored in plain text

### 3. Authorization Checks
- `get_current_user()`: Returns 401 if token missing/invalid
- `require_admin()`: Returns 403 if user is not admin
- Product validation: Returns 404 if product_id doesn't exist

### 4. Database Constraints
- Unique constraints on email and username
- Foreign key constraints on user_id and product_id
- Indexed columns for performance (user_id, product_id, status, created_at)

---

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Database Migration
```bash
flask db upgrade
```

This will create the `users` and `reports` tables.

### 3. Start the API
```bash
flask run
```

---

## Testing the API

### Using cURL

#### 1. Register a User
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

#### 2. Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```
**Save the `access_token` from response**

#### 3. Create a Report
```bash
curl -X POST http://localhost:5000/reports \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "message": "This product is problematic",
    "evidence_url": "https://example.com/proof"
  }'
```

#### 4. Get My Reports
```bash
curl -X GET http://localhost:5000/reports/mine \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## File Structure

```
backend/
├── models/
│   ├── user.py              # User model with password hashing
│   ├── report.py            # Report model
│   └── __init__.py
├── resources/
│   ├── auth.py              # Register/Login endpoints
│   ├── reports.py           # Reports CRUD endpoints
│   └── ...
├── auth.py                  # JWT utilities & auth dependencies
├── schema.py                # Marshmallow schemas (updated with auth/report schemas)
├── app.py                   # Main Flask app (updated to include new blueprints)
├── requirements.txt         # Dependencies (updated with PyJWT)
├── migrations/
│   └── versions/
│       └── add_auth_reports.py  # Migration script for new tables
└── config.py
```

---

## Important Security Notes

1. **Secret Key**: In production, never hardcode `SECRET_KEY` in config.py. Use environment variables:
   ```python
   # config.py
   import os
   SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
   ```

2. **HTTPS Only**: Always use HTTPS in production. Tokens can be intercepted if sent over HTTP.

3. **Token Expiration**: Currently set to 24 hours. Adjust in `auth.py` if needed:
   ```python
   create_access_token(user.id, user.role, expires_in=3600)  # 1 hour
   ```

4. **Rate Limiting**: Consider adding rate limiting to auth endpoints to prevent brute force attacks.

5. **Admin Creation**: Manually create admin users in the database:
   ```python
   # In Flask shell
   from models.user import User
   from db import db
   
   admin = User(username="admin", email="admin@example.com", role="admin")
   admin.set_password("secure_password")
   db.session.add(admin)
   db.session.commit()
   ```

---

## Troubleshooting

### "ImportError: No module named 'jwt'"
Run: `pip install PyJWT`

### "401 Unauthorized" even with valid token
- Ensure token format is `Authorization: Bearer <token>` (with space)
- Check token hasn't expired
- Verify `SECRET_KEY` in config.py matches the one used to create the token

### "403 Forbidden" on admin endpoints
- Ensure user has `role="admin"` in the database
- Manually update: `UPDATE users SET role='admin' WHERE id=1;`

### Migration fails
- Ensure `flask db upgrade` is run after creating new models
- Check that PostgreSQL is running and accessible

---

## Next Steps (Optional Enhancements)

1. **Email Verification**: Add email confirmation on registration
2. **Refresh Tokens**: Implement refresh token flow for better security
3. **Rate Limiting**: Protect auth endpoints with rate limiting
4. **Audit Logging**: Log all report status changes for compliance
5. **Webhooks**: Notify users when their reports are reviewed
6. **Search**: Full-text search for reports by message content
7. **Pagination**: Add pagination to GET /reports endpoint
8. **Soft Deletes**: Archive reports instead of deleting them

---

## Architecture Diagram

```
User Request
    ↓
[Authorization Header (Bearer Token)]
    ↓
auth.py: get_current_user() / require_admin()
    ↓
[Validate JWT]
    ↓
Return User Object OR 401/403 Error
    ↓
Endpoint Handler (resources/reports.py)
    ↓
Database Operation (SQLAlchemy)
    ↓
JSON Response (Marshmallow Schema)
```

---

## Public vs Protected Endpoints

| Endpoint | Auth Required | Admin Only | Public |
|----------|---------------|-----------|--------|
| GET /products | ❌ | ❌ | ✅ |
| GET /products/{id} | ❌ | ❌ | ✅ |
| GET /products/search | ❌ | ❌ | ✅ |
| POST /auth/register | ❌ | ❌ | ✅ |
| POST /auth/login | ❌ | ❌ | ✅ |
| POST /reports | ✅ | ❌ | ❌ |
| GET /reports/mine | ✅ | ❌ | ❌ |
| GET /reports | ✅ | ✅ | ❌ |
| PUT /reports/{id} | ✅ | ✅ | ❌ |

---

This implementation demonstrates proper authentication and authorization patterns while keeping your public product endpoints accessible.
