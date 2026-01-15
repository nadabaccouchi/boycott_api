from flask.views import MethodView
from flask_smorest import Blueprint
from models.product import Product
from models.brand import Brand
from schema import ProductSchema

blp = Blueprint("Search", __name__, description="Search endpoints")

@blp.route("/search/<string:query>")
class Search(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self, query):
        products_by_name = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
        matching_brands = Brand.query.filter(Brand.name.ilike(f"%{query}%")).all()

        products_by_brand = []
        for b in matching_brands:
            products_by_brand.extend(b.products)

        # remove duplicates by product id
        all_products = {p.id: p for p in (products_by_name + products_by_brand)}
        return list(all_products.values())
