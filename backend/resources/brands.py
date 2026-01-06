from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.brand import Brand
from schema import BrandSchema

blp = Blueprint("Brands", __name__, description="Brands endpoints")

@blp.route("/brands")
class BrandList(MethodView):
    @blp.response(200, BrandSchema(many=True))
    def get(self):
        return Brand.query.all()

@blp.route("/brands/<int:brand_id>")
class BrandDetail(MethodView):
    @blp.response(200, BrandSchema)
    def get(self, brand_id):
        brand = Brand.query.get(brand_id)
        if not brand:
            abort(404, message="Brand not found")
        return brand
