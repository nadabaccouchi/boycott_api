# FILE: resources/barcode.py

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from models.product import Product
from models.brand_alternative import BrandAlternative
from schema import BarcodeResultSchema  # keep your import name as-is

blp = Blueprint("Barcode", __name__, description="Barcode lookup")


def brand_to_dict(b):
    return {
        "id": b.id,
        "name": b.name,
        "website": b.website,
        "logo_url": b.logo_url,
        "boycott_status": b.boycott_status,
        "reason": b.reason,
    }


def validate_barcode_or_400(barcode: str) -> None:
    # Digits only
    if not barcode.isdigit():
        abort(400, message="Invalid barcode format: digits only.")

    # Common barcode lengths (EAN-8, UPC-A, EAN-13, ITF-14)
    if len(barcode) not in (8, 12, 13, 14):
        abort(400, message="Invalid barcode length: must be 8, 12, 13, or 14 digits.")


@blp.route("/barcode/<string:barcode>")
class BarcodeLookup(MethodView):
    @blp.response(200, BarcodeResultSchema)
    def get(self, barcode):
        """
        GET /barcode/{barcode}
        """
        # 1) Interaction design + constraints: validate input early -> 400
        validate_barcode_or_400(barcode)

        product = Product.query.filter_by(barcode=barcode).first()
        if not product:
            abort(404, message="Product not found.")

        brand = product.brand
        if not brand:
            # Data integrity issue -> server-side error
            abort(500, message="Product has no brand.")

        # Not boycotted → return empty alternatives (still a valid flow)
        if not brand.boycott_status:
            return {
                "barcode": product.barcode,
                "product_name": product.name,
                "brand": brand_to_dict(brand),
                "alternatives": [],
            }

        # Product categories (many-to-many)
        product_category_ids = [c.id for c in (product.categories or [])]

        q = BrandAlternative.query.filter(
            BrandAlternative.boycotted_brand_id == brand.id
        )

        # Filter alternatives by product categories when available;
        # also allow "global" alternatives where category_id is NULL
        if product_category_ids:
            q = q.filter(
                (BrandAlternative.category_id.in_(product_category_ids))
                | (BrandAlternative.category_id.is_(None))
            )
        else:
            q = q.filter(BrandAlternative.category_id.is_(None))

        links = q.order_by(BrandAlternative.score.desc()).all()

        alternatives = [
            brand_to_dict(link.alternative_brand)
            for link in links
            if link.alternative_brand
        ]

        return {
            "barcode": product.barcode,
            "product_name": product.name,
            "brand": brand_to_dict(brand),
            "alternatives": alternatives,
        }
