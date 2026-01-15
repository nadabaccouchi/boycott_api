from db import db
from models.product import product_category

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)

    products = db.relationship(
        "Product",
        secondary=product_category,
        back_populates="categories",
    )
