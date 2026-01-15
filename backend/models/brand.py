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

    # Links where THIS brand is the boycotted one (recommended alternatives)
    alternative_links = db.relationship(
        "BrandAlternative",
        foreign_keys="BrandAlternative.boycotted_brand_id",
        back_populates="boycotted_brand",
        cascade="all, delete-orphan",
    )

    # Links where THIS brand is used as an alternative for other brands
    as_alternative_for_links = db.relationship(
        "BrandAlternative",
        foreign_keys="BrandAlternative.alternative_brand_id",
        back_populates="alternative_brand",
        cascade="all, delete-orphan",
    )
