from db import db

class Brand(db.Model):
    __tablename__ = "brands"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    website = db.Column(db.String(200))
    logo_url = db.Column(db.String(300))
    boycott_status = db.Column(db.Boolean, default=False)
    reason = db.Column(db.String(500))

    products = db.relationship("Product", back_populates="brand")
    alternatives = db.relationship("Alternative", back_populates="brand")
