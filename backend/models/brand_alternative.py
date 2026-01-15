from db import db

class BrandAlternative(db.Model):
    __tablename__ = "brand_alternatives"

    id = db.Column(db.Integer, primary_key=True)

    boycotted_brand_id = db.Column(
        db.Integer, db.ForeignKey("brands.id"), nullable=False
    )

    alternative_brand_id = db.Column(
        db.Integer, db.ForeignKey("brands.id"), nullable=False
    )

    # Optional: category-specific alternative
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    # Optional: ranking (higher is better)
    score = db.Column(db.Integer, default=100, nullable=False)

    # Optional: explanation like "local", "same quality", etc.
    note = db.Column(db.String(250), nullable=True)

    boycotted_brand = db.relationship(
        "Brand",
        foreign_keys=[boycotted_brand_id],
        back_populates="alternative_links",
    )

    alternative_brand = db.relationship(
        "Brand",
        foreign_keys=[alternative_brand_id],
        back_populates="as_alternative_for_links",
    )

    category = db.relationship("Category")
