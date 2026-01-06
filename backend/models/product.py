from db import db

# Association table for many-to-many relationship between Product and Category
product_category = db.Table(
    "product_category",
    db.Column("product_id", db.Integer, db.ForeignKey("products.id")),
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id"))
)

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    barcode = db.Column(db.String(50), unique=True, nullable=False)

    # Foreign key for Brand
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=False)
    brand = db.relationship("Brand", back_populates="products")

    # Many-to-many relationship with Category
    categories = db.relationship(
        "Category",
        secondary=product_category,  # This is the association table
        backref="products"
    )

    # Relationship with Alternative
    alternatives = db.relationship("Alternative", back_populates="original_product")
