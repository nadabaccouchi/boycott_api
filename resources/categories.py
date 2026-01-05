from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models.category import Category
from schema import CategorySchema, ProductSchema
from models.product import Product

blp = Blueprint("Categories", __name__, description="Categories endpoints")

@blp.route("/categories")
class CategoryList(MethodView):
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        return Category.query.all()

@blp.route("/categories/<string:slug>/products")
class CategoryProducts(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self, slug):
        category = Category.query.filter_by(slug=slug).first()
        if not category:
            abort(404, message="Category not found")
        return category.products
