# FILE: resources/brands.py

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy import asc, desc
from sqlalchemy.exc import IntegrityError

from db import db
from models.brand import Brand
from models.product import Product
from models.category import Category
from schema import BrandSchema, BrandCreateUpdateSchema
import auth_utils as auth_module


blp = Blueprint("Brands", __name__, description="Brands endpoints")


@blp.route("/brands")
class BrandList(MethodView):
    @blp.doc(
        parameters=[
            {
                "in": "query",
                "name": "search",
                "schema": {"type": "string"},
                "required": False,
                "description": "Search brands by name. Example: ?search=danone",
            },
            {
                "in": "query",
                "name": "boycott_status",
                "schema": {"type": "boolean"},
                "required": False,
                "description": "Filter by boycott status. Example: ?boycott_status=true",
            },
            {
                "in": "query",
                "name": "category_id",
                "schema": {"type": "integer"},
                "required": False,
                "description": "Filter brands that have products in a category. Example: ?category_id=3",
            },
            {
                "in": "query",
                "name": "sort",
                "schema": {"type": "string", "enum": ["name"]},
                "required": False,
                "description": "Sort brands (only supported value: name).",
            },
            {
                "in": "query",
                "name": "order",
                "schema": {"type": "string", "enum": ["asc", "desc"]},
                "required": False,
                "description": "Sort order: asc (A–Z) or desc (Z–A).",
            },
            {
                "in": "query",
                "name": "page",
                "schema": {"type": "integer"},
                "required": False,
                "description": "Page number (starts at 1). Example: ?page=1",
            },
            {
                "in": "query",
                "name": "limit",
                "schema": {"type": "integer"},
                "required": False,
                "description": "Max results per page (max 100). Example: ?limit=20",
            },
        ]
    )
    @blp.response(200, BrandSchema(many=True))
    def get(self):
        """
        GET /brands
        """
        query = Brand.query

        # --- Filtering: search ---
        search = request.args.get("search", type=str)
        if search:
            query = query.filter(Brand.name.ilike(f"%{search}%"))

        # --- Filtering: boycott_status (accept true/false) ---
        boycott_status_raw = request.args.get("boycott_status")
        if boycott_status_raw is not None:
            val = boycott_status_raw.strip().lower()
            if val in ("true", "1", "yes"):
                query = query.filter(Brand.boycott_status.is_(True))
            elif val in ("false", "0", "no"):
                query = query.filter(Brand.boycott_status.is_(False))
            else:
                abort(400, message="Invalid boycott_status. Use true or false.")

        # --- Filtering: category_id (brands that have products in this category) ---
        category_id = request.args.get("category_id", type=int)
        if category_id is not None:
            if category_id < 1:
                abort(400, message="category_id must be >= 1.")

            query = (
                query.join(Brand.products)
                     .join(Product.categories)
                     .filter(Category.id == category_id)
                     .distinct()
            )

        # --- Sorting ---
        sort = request.args.get("sort", default="name", type=str)
        order = request.args.get("order", default="asc", type=str)

        if sort != "name":
            abort(400, message="Invalid sort field. Only 'name' is supported.")
        if order not in ("asc", "desc"):
            abort(400, message="Invalid order. Use 'asc' or 'desc'.")

        direction = asc if order == "asc" else desc
        query = query.order_by(direction(Brand.name), Brand.id.asc())

        # --- Pagination ---
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=20, type=int)

        if page < 1:
            abort(400, message="page must be >= 1.")
        if limit < 1 or limit > 100:
            abort(400, message="limit must be between 1 and 100.")

        return query.offset((page - 1) * limit).limit(limit).all()

    # ✅ CREATE brand (admin later)
    @blp.arguments(BrandCreateUpdateSchema())
    @blp.doc(security=[{"BearerAuth": []}])
    @blp.response(201, BrandSchema())
    def post(self, data):
        """
        POST /brands
        Admin only.
        """
        admin = auth_module.require_admin()

        brand = Brand(**data)
        db.session.add(brand)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Brand with this name already exists.")
        return brand


@blp.route("/brands/<int:brand_id>")
class BrandDetail(MethodView):
    @blp.response(200, BrandSchema())
    def get(self, brand_id):
        """
        GET /brands/{id}
        """
        brand = Brand.query.get(brand_id)
        if not brand:
            abort(404, message="Brand not found.")
        return brand

    # ✅ UPDATE brand (admin later)
    @blp.arguments(BrandCreateUpdateSchema(partial=True))
    @blp.doc(security=[{"BearerAuth": []}])
    @blp.response(200, BrandSchema())
    def put(self, data, brand_id):
        """
        PUT /brands/{id}
        Admin only.
        """
        auth_module.require_admin()
        brand = Brand.query.get(brand_id)
        if not brand:
            abort(404, message="Brand not found.")

        for k, v in data.items():
            setattr(brand, k, v)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Brand with this name already exists.")
        return brand

    # ✅ DELETE brand (admin later)
    @blp.doc(security=[{"BearerAuth": []}])
    def delete(self, brand_id):
        """
        DELETE /brands/{id}
        Admin only.
        """
        auth_module.require_admin()
        brand = Brand.query.get(brand_id)
        if not brand:
            abort(404, message="Brand not found.")
        db.session.delete(brand)
        db.session.commit()
        return {"message": "Brand deleted."}, 200
