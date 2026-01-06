from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.product import Product
from models.brand import Brand
from schema import ProductSchema, BrandSchema

blp = Blueprint("Search", __name__, description="Search endpoints")

@blp.route("/search/<string:query>")
class Search(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self, query):
        products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
        brands = Brand.query.filter(Brand.name.ilike(f"%{query}%")).all()

        # Combine results
        return products + [b.products[0] for b in brands if b.products]
