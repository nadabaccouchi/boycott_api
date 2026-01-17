# FILE: resources/categories.py

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError

from db import db
from models.category import Category
from schema import CategorySchema, CategoryCreateUpdateSchema, ProductSchema
import auth_utils as auth_module

blp = Blueprint("Categories", __name__, description="Categories endpoints")


@blp.route("/categories")
class CategoryList(MethodView):
    @blp.response(200, CategorySchema(many=True))
    def get(self):
        """
        GET /categories
        """
        return Category.query.order_by(Category.name.asc(), Category.id.asc()).all()

    # ✅ CREATE category (admin later)
    @blp.arguments(CategoryCreateUpdateSchema())
    @blp.doc(security=[{"BearerAuth": []}])
    @blp.response(201, CategorySchema())
    @auth_module.admin_required
    def post(self, data):
        """
        POST /categories
        Admin only.
        """
        category = Category(**data)
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Category slug must be unique.")
        return category


@blp.route("/categories/<int:category_id>")
class CategoryDetail(MethodView):
    @blp.response(200, CategorySchema())
    def get(self, category_id):
        """
        GET /categories/{id}
        """
        category = Category.query.get(category_id)
        if not category:
            abort(404, message="Category not found.")
        return category

    # ✅ UPDATE category (admin later)
    @blp.arguments(CategoryCreateUpdateSchema(partial=True))
    @blp.doc(security=[{"BearerAuth": []}])
    @blp.response(200, CategorySchema())
    @auth_module.admin_required
    def put(self, data, category_id):
        """
        PUT /categories/{id}
        Admin only.
        """
        category = Category.query.get(category_id)
        if not category:
            abort(404, message="Category not found.")

        for k, v in data.items():
            setattr(category, k, v)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Category slug must be unique.")
        return category

    # ✅ DELETE category (admin later)
    @blp.doc(security=[{"BearerAuth": []}])
    @auth_module.admin_required
    def delete(self, category_id):
        """
        DELETE /categories/{id}
        Admin only.
        """
        category = Category.query.get(category_id)
        if not category:
            abort(404, message="Category not found.")
        db.session.delete(category)
        db.session.commit()
        return {"message": "Category deleted."}, 200


@blp.route("/categories/<string:slug>/products")
class CategoryProducts(MethodView):
    @blp.response(200, ProductSchema(many=True))
    def get(self, slug):
        category = Category.query.filter_by(slug=slug).first()
        if not category:
            abort(404, message="Category not found.")
        return category.products
