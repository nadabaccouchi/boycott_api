from flask.views import MethodView
from flask_smorest import Blueprint, abort

from models.product import Product
from models.brand_alternative import BrandAlternative
from schema import BarcodeResultSchema

blp = Blueprint("Barcode", __name__, description="Barcode lookup")

@blp.route("/barcode/<string:barcode>")
class BarcodeLookup(MethodView):
    @blp.response(200, BarcodeResultSchema)
    def get(self, barcode):
        # 1) Only search inside YOUR DB
        product = Product.query.filter_by(barcode=barcode).first()
        if not product:
            abort(404, message="Barcode not found in dataset")

        brand = product.brand

        # 2) If not boycotted => no alternatives
        if not brand.boycott_status:
            return {
                "barcode": product.barcode,
                "product_name": product.name,
                "brand": brand,
                "alternatives": [],
            }

        # 3) If boycotted => return alternative BRANDS
        product_category_ids = [c.id for c in product.categories]

        # Get category-specific alternatives first, then general ones (category_id = NULL)
        q = BrandAlternative.query.filter(
            BrandAlternative.boycotted_brand_id == brand.id
        )

        if product_category_ids:
            q = q.filter(
                (BrandAlternative.category_id.in_(product_category_ids)) |
                (BrandAlternative.category_id.is_(None))
            )
        else:
            # If product has no category, only general alternatives
            q = q.filter(BrandAlternative.category_id.is_(None))

        links = q.order_by(BrandAlternative.score.desc()).all()

        alternatives = [link.alternative_brand for link in links]

        return {
            "barcode": product.barcode,
            "product_name": product.name,
            "brand": brand,
            "alternatives": alternatives,
        }
