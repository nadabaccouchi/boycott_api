from db import db

product_category = db.Table(
    "product_category",
    db.Column("product_id", db.Integer, db.ForeignKey("products.id"), primary_key=True),
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id"), primary_key=True),
)

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    barcode = db.Column(db.String(50), unique=True, nullable=False)

    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
    brand = db.relationship("Brand", back_populates="products")

    categories = db.relationship(
        "Category",
        secondary=product_category,
        back_populates="products",
    )
