from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.product import Product
from schema import ProductSchema
from marshmallow import Schema, fields

blp = Blueprint("Products", __name__, description="Products endpoints")

@blp.route("/products")
class ProductList(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        return Product.query.all()

@blp.route("/products/<string:barcode>/alternatives")
class ProductAlternatives(MethodView):
    @blp.response(200, fields.List(fields.Nested(ProductSchema)))
    def get(self, barcode):
        product = Product.query.filter_by(barcode=barcode).first()
        if not product:
            abort(404, message="Product not found")
        return product.alternatives
