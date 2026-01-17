# Code Examples & Architecture

## File Organization

```
backend/
├── models/
│   ├── __init__.py (exports all models)
│   ├── user.py (User model with password hashing)
│   ├── report.py (Report model)
│   ├── product.py (existing)
│   └── ...
│
├── resources/
│   ├── auth.py (Register & Login endpoints)
│   ├── reports.py (Reports CRUD endpoints)
│   ├── products.py (existing)
│   └── ...
│
├── migrations/
│   ├── versions/
│   │   ├── add_auth_reports.py (New tables)
│   │   └── ...existing migrations
│   └── ...
│
├── auth.py (JWT utilities & dependencies)
├── schema.py (Marshmallow schemas - UPDATED)
├── app.py (Main Flask app - UPDATED)
├── db.py
├── config.py
└── requirements.txt (UPDATED)
```

---

## Code Examples

### 1. Creating a User (models/user.py)

```python
from db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
```

### 2. JWT Authentication (auth.py)

```python
import jwt
from datetime import datetime, timedelta
from flask import current_app

def create_access_token(user_id, user_role, expires_in=86400):
    """Create JWT token (24 hours default)"""
    payload = {
        "user_id": user_id,
        "user_role": user_role,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
    }
    token = jwt.encode(
        payload, 
        current_app.config["SECRET_KEY"], 
        algorithm="HS256"
    )
    return token

def get_current_user():
    """Extract and validate JWT from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        abort(401, message="Missing authorization header.")
    
    scheme, token = auth_header.split()
    if scheme.lower() != "bearer":
        abort(401, message="Invalid authorization scheme.")
    
    payload = decode_token(token)
    if not payload:
        abort(401, message="Invalid or expired token.")
    
    user = User.query.get(payload.get("user_id"))
    return user

def require_admin():
    """Check if current user is admin"""
    user = get_current_user()
    if user.role != "admin":
        abort(403, message="Admin access required.")
    return user
```

### 3. Register Endpoint (resources/auth.py)

```python
@blp.route("/auth/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema())
    @blp.response(201, AuthResponseSchema())
    def post(self, data):
        """Register new user"""
        # Check if user exists
        if User.query.filter_by(email=data["email"]).first():
            abort(409, message="Email already registered.")
        
        # Create user
        user = User(
            username=data["username"],
            email=data["email"],
            role="user"  # Default role
        )
        user.set_password(data["password"])
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = create_access_token(user.id, user.role)
        
        return {
            "access_token": token,
            "user": user.to_dict()
        }
```

### 4. Create Report Endpoint (resources/reports.py)

```python
@blp.route("/reports")
class ReportList(MethodView):
    @blp.arguments(ReportCreateSchema())
    @blp.response(201, ReportSchema())
    def post(self, data):
        """Create new report (auth required)"""
        user = get_current_user()  # Dependency
        
        # Validate product exists if provided
        if data.get("product_id"):
            product = Product.query.get(data["product_id"])
            if not product:
                abort(404, message="Product not found.")
        
        # Create report
        report = Report(
            user_id=user.id,
            product_id=data.get("product_id"),
            barcode=data.get("barcode"),
            message=data["message"],
            evidence_url=data.get("evidence_url"),
            status="pending"  # Default status
        )
        
        db.session.add(report)
        db.session.commit()
        return report
```

### 5. Admin Report Review (resources/reports.py)

```python
@blp.route("/reports/<int:report_id>")
class ReportDetail(MethodView):
    @blp.arguments(ReportUpdateSchema())
    @blp.response(200, ReportSchema())
    def put(self, data, report_id):
        """Update report (admin only)"""
        admin = require_admin()  # Dependency - returns 403 if not admin
        
        report = Report.query.get(report_id)
        if not report:
            abort(404, message="Report not found.")
        
        # Update status
        report.status = data["status"]  # approved or rejected
        
        # Add admin note if provided
        if "admin_note" in data:
            report.admin_note = data["admin_note"]
        
        db.session.commit()
        return report
```

### 6. Schema Validation (schema.py)

```python
class ReportCreateSchema(Schema):
    """Validate report creation input"""
    product_id = fields.Int(allow_none=True)
    barcode = fields.Str(
        allow_none=True,
        validate=validate.Regexp(r"^\d{8,14}$")
    )
    message = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=2000)
    )
    evidence_url = fields.Str(
        allow_none=True,
        validate=validate.URL()
    )
    
    @validates_schema
    def validate_product_or_barcode(self, data, **kwargs):
        """Ensure either product_id or barcode is provided"""
        if not data.get("product_id") and not data.get("barcode"):
            raise ValidationError(
                "Either product_id or barcode must be provided."
            )
```

### 7. Report Model (models/report.py)

```python
from enum import Enum as PyEnum

class ReportStatus(PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Report(db.Model):
    __tablename__ = "reports"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    barcode = db.Column(db.String(14), nullable=True)
    message = db.Column(db.Text, nullable=False)
    evidence_url = db.Column(db.String(500), nullable=True)
    status = db.Column(
        db.String(20),
        default=ReportStatus.PENDING.value,
        nullable=False
    )
    admin_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    user = db.relationship("User", backref="reports")
    product = db.relationship("Product", backref="reports")
```

### 8. App Registration (app.py)

```python
from resources.auth import blp as auth_blp
from resources.reports import blp as reports_blp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    Migrate(app, db)
    
    api = Api(app)
    
    # Register blueprints
    api.register_blueprint(auth_blp)      # /auth endpoints
    api.register_blueprint(reports_blp)   # /reports endpoints
    # ... other blueprints
    
    return app
```

---

## Request/Response Flow

### 1. Registration Flow

```
POST /auth/register
├── Body: {username, email, password}
├── Schema validation ✓
├── Check email uniqueness ✓
├── Hash password with Werkzeug
├── Create User record
├── Generate JWT token
└── Response: {access_token, user}
```

### 2. Report Creation Flow

```
POST /reports
├── Extract JWT from Authorization header
├── Decode and validate token
├── Get User from database ✓
├── Schema validation ✓
├── Check product_id exists (if provided) ✓
├── Create Report with user_id and status="pending"
├── Save to database
└── Response: Report object (201 Created)
```

### 3. Admin Report Review Flow

```
PUT /reports/{id}
├── Extract JWT from Authorization header
├── Validate token
├── Get User from database
├── Check user.role == "admin" (403 if not)
├── Schema validation ✓
├── Update status and admin_note
├── Save to database
└── Response: Updated report object (200 OK)
```

---

## Dependency Injection Pattern

The API uses Flask's dependency pattern for auth:

```python
# In any endpoint
@blp.route("/protected")
class Protected(MethodView):
    def get(self):
        # Call dependency functions in handler
        user = get_current_user()  # Returns User or 401
        
        # Access user data
        return {"user_id": user.id, "role": user.role}

@blp.route("/admin-only")
class AdminOnly(MethodView):
    def get(self):
        # Call dependency that checks admin role
        admin = require_admin()  # Returns User or 403
        
        return {"admin": admin.username}
```

---

## Database Relationships

```
User (1) ←→ (many) Report
  ├─ id ────────→ report.user_id
  └─ reports (backref)

Product (1) ←→ (many) Report
  ├─ id ────────→ report.product_id (nullable)
  └─ reports (backref)
```

---

## Security Layers

```
Request
  ↓
1. JWT Extraction & Validation
   └─ Missing header? → 401
   └─ Invalid format? → 401
   └─ Expired token? → 401
   └─ Invalid signature? → 401
  ↓
2. Database Lookup
   └─ User not found? → 401
  ↓
3. Role Check (if required)
   └─ role != "admin"? → 403
  ↓
4. Schema Validation
   └─ Invalid data? → 400
  ↓
5. Business Logic Validation
   └─ Product not found? → 404
   └─ Email exists? → 409
  ↓
6. Database Operation
  ↓
Response (200/201/400/401/403/404/409)
```

---

This implementation demonstrates professional patterns for:
- ✅ Authentication (JWT)
- ✅ Authorization (Role-based)
- ✅ Validation (Marshmallow)
- ✅ Error Handling (HTTP status codes)
- ✅ Database Design (Foreign keys, constraints)
- ✅ Code Organization (Models, Resources, Schemas, Auth)
