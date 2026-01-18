# FILE: resources/barcode.py

from decimal import Decimal, InvalidOperation
from urllib.parse import unquote

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import cast, Numeric

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


def clean_barcode_input(raw: str) -> str:
    s = raw if raw is not None else ""
    s = unquote(s)
    s = s.strip()
    s = "".join(s.split())

    # Remove common separators
    s = s.replace(",", "").replace("_", "")
    return s


def normalize_barcode_or_400(raw: str) -> str:
    # Decode URL encoding and strip whitespace
    s = clean_barcode_input(raw)

    # Digits only -> validate length
    if s.isdigit():
        if len(s) not in (8, 12, 13, 14):
            abort(400, message="Invalid barcode length: must be 8, 12, 13, or 14 digits.")
        return s

    # Scientific notation or decimal -> parse safely with Decimal
    if ("e" in s.lower()) or ("." in s):
        try:
            d = Decimal(s)
            if d != d.to_integral_value():
                abort(400, message="Invalid barcode format: must be an integer.")
            d = d.to_integral_value()
            # Convert scientific notation to plain digits
            s = format(d, "f")
        except (InvalidOperation, ValueError):
            abort(400, message="Invalid barcode format: digits only.")
    else:
        abort(400, message="Invalid barcode format: digits only.")

    if not s.isdigit():
        abort(400, message="Invalid barcode format: digits only.")
    if len(s) not in (8, 12, 13, 14):
        abort(400, message="Invalid barcode length: must be 8, 12, 13, or 14 digits.")

    return s


def format_barcode_for_output(raw: str) -> str:
    s = clean_barcode_input(raw)
    if s.isdigit():
        return s
    if ("e" in s.lower()) or ("." in s):
        try:
            d = Decimal(s)
        except (InvalidOperation, ValueError):
            return str(raw)
        if d != d.to_integral_value():
            return str(raw)
        return format(d.to_integral_value(), "f")
    return str(raw)


# Accept characters like "+" and "e" in the path
@blp.route("/barcode/<path:barcode>")
class BarcodeLookup(MethodView):
    @blp.response(200, BarcodeResultSchema)
    def get(self, barcode):
        """
        GET /barcode/{barcode}
        """
        # Normalize input to digits only
        raw_clean = clean_barcode_input(barcode)
        product = Product.query.filter_by(barcode=raw_clean).first()

        if product:
            barcode = format_barcode_for_output(product.barcode)
        else:
            barcode = normalize_barcode_or_400(raw_clean)
            product = Product.query.filter(
                (Product.barcode.in_([barcode, raw_clean]))
                | (cast(Product.barcode, Numeric) == int(barcode))
            ).first()
        if not product:
            abort(404, message="Product not found.")

        brand = product.brand
        if not brand:
            # Data integrity issue -> server-side error
            abort(500, message="Product has no brand.")

        # Not boycotted → return empty alternatives (still a valid flow)
        if not brand.boycott_status:
            return {
                "barcode": barcode,
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
            "barcode": barcode,
            "product_name": product.name,
            "brand": brand_to_dict(brand),
            "alternatives": alternatives,
        }
