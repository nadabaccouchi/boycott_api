from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.product import Product
from models.brand import Brand
from db import db
from schema import ProductSchema

blp = Blueprint("Barcode", __name__, description="Barcode lookup")

@blp.route("/barcode/<string:barcode>")
class BarcodeLookup(MethodView):
    @blp.response(200, ProductSchema)
    def get(self, barcode):
        # Check if the product exists in the database
        product = Product.query.filter_by(barcode=barcode).first()
        if product:
            return product

        # If not found, query external API to check boycott status
        data = check_boycott(barcode)
        if not data:
            abort(404, message="Product not found in boycott sources")

        # If brand doesn't exist in DB, create a new one
        brand = Brand.query.filter_by(name=data["brand"]).first()
        if not brand:
            brand = Brand(name=data["brand"], boycott_status=True)
            db.session.add(brand)

        # Create a new product with the information from the external API
        product = Product(
            name=data["name"],
            barcode=barcode,
            brand=brand
        )
        db.session.add(product)
        db.session.commit()

        # Add alternatives for the product
        alternatives = get_tunisian_alternatives(product)
        product.alternatives = alternatives

        return product
