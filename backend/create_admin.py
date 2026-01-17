from app import app
from db import db
from models.user import User

ADMIN_EMAIL = "admin@admin.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin123456"

with app.app_context():
    u = User.query.filter_by(email=ADMIN_EMAIL).first()
    if not u:
        u = User(username=ADMIN_USERNAME, email=ADMIN_EMAIL, role="admin")
        u.set_password(ADMIN_PASSWORD)
        db.session.add(u)
        db.session.commit()
        print("Admin created:", ADMIN_EMAIL)
    else:
        u.role = "admin"
        u.set_password(ADMIN_PASSWORD)
        db.session.commit()
        print("Existing user upgraded to admin:", ADMIN_EMAIL)
