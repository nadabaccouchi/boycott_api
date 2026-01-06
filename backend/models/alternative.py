from db import db

class Alternative(db.Model):
    __tablename__ = "alternatives"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    website = db.Column(db.String(200))
    logo_url = db.Column(db.String(300))

    # Foreign key for Brand
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
    brand = db.relationship("Brand", back_populates="alternatives")

    # Foreign key for Product
    original_product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    original_product = db.relationship("Product", back_populates="alternatives")
