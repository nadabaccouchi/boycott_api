from flask.views import MethodView
from flask_smorest import Blueprint, abort

from models.product import Product
from models.brand_alternative import BrandAlternative
from schema import ProductSchema, BrandSchema

blp = Blueprint("Products", __name__, description="Products endpoints")

@blp.route("/products")
class ProductList(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        return Product.query.all()

@blp.route("/products/<string:barcode>/alternatives")
class ProductBrandAlternatives(MethodView):
    @blp.response(200, BrandSchema(many=True))
    def get(self, barcode):
        product = Product.query.filter_by(barcode=barcode).first()
        if not product:
            abort(404, message="Product not found")

        brand = product.brand

        if not brand.boycott_status:
            return []

        product_category_ids = [c.id for c in product.categories]

        q = BrandAlternative.query.filter(
            BrandAlternative.boycotted_brand_id == brand.id
        )

        if product_category_ids:
            q = q.filter(
                (BrandAlternative.category_id.in_(product_category_ids)) |
                (BrandAlternative.category_id.is_(None))
            )
        else:
            q = q.filter(BrandAlternative.category_id.is_(None))

        links = q.order_by(BrandAlternative.score.desc()).all()
        return [link.alternative_brand for link in links]
