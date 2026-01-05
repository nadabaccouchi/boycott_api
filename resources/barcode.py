from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.product import Product
from models.brand import Brand
from db import db
from schema import ProductSchema
from services.boycott_service import check_boycott
from services.alternative_engine import get_tunisian_alternatives


blp = Blueprint("Barcode", __name__, description="Barcode lookup")

@blp.route("/barcode/<string:barcode>")
class BarcodeLookup(MethodView):
    @blp.response(200, ProductSchema)
    def get(self, barcode):

        product = Product.query.filter_by(barcode=barcode).first()
        if product:
            return product

        # Not in DB → query external API
        data = check_boycott(barcode)
        if not data:
            abort(404, message="Product not found in boycott sources")

        brand = Brand.query.filter_by(name=data["brand"]).first()
        if not brand:
            brand = Brand(name=data["brand"], boycott_status=True)
            db.session.add(brand)

        product = Product(
            name=data["name"],
            barcode=barcode,
            brand=brand
        )

        db.session.add(product)
        db.session.commit()

        alternatives = get_tunisian_alternatives(product)
        product.alternatives = alternatives


        return product
