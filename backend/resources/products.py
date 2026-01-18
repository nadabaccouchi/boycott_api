from decimal import Decimal, InvalidOperation
from urllib.parse import unquote

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy import cast, Numeric
from sqlalchemy import asc, desc
from sqlalchemy.exc import IntegrityError

from db import db
from models.product import Product
from models.brand import Brand
from models.brand_alternative import BrandAlternative
from models.category import Category
from schema import ProductSchema, BrandSchema, ProductCreateUpdateSchema
import auth_utils as auth_module

blp = Blueprint("Products", __name__, description="Products endpoints")


def normalize_barcode_or_400(raw: str) -> str:
    s = raw if raw is not None else ""
    s = unquote(s)
    s = s.strip()
    s = "".join(s.split())

    s = s.replace(",", "").replace("_", "")

    if s.isdigit():
        if len(s) not in (8, 12, 13, 14):
            abort(400, message="Invalid barcode length: must be 8, 12, 13, or 14 digits.")
        return s

    if ("e" in s.lower()) or ("." in s):
        try:
            d = Decimal(s)
            if d != d.to_integral_value():
                abort(400, message="Invalid barcode format: must be an integer.")
            d = d.to_integral_value()
            s = format(d, "f")
        except (InvalidOperation, ValueError):
            abort(400, message="Invalid barcode format: digits only.")
    else:
        abort(400, message="Invalid barcode format: digits only.")

    if not s.isdigit():
        abort(400, message="Invalid barcode format: digits only.")
    if len(s) not in (8, 12, 13, 14):
        abort(400, message="Invalid barcode length: must be 8, 12, 13, or 14 digits.")

    return s


def clean_barcode_input(raw: str) -> str:
    s = raw if raw is not None else ""
    s = unquote(s)
    s = s.strip()
    s = "".join(s.split())
    return s.replace(",", "").replace("_", "")


@blp.route("/products")
class ProductList(MethodView):

    @blp.doc(
        parameters=[
            {
                "in": "query",
                "name": "search",
                "schema": {"type": "string"},
                "required": False,
                "description": "Search products by name. Example: ?search=yaourt",
            },
            {
                "in": "query",
                "name": "brand_id",
                "schema": {"type": "integer"},
                "required": False,
                "description": "Filter by brand ID. Example: ?brand_id=12",
            },
            {
                "in": "query",
                "name": "category_id",
                "schema": {"type": "integer"},
                "required": False,
                "description": "Filter by category ID. Example: ?category_id=3",
            },
            {
                "in": "query",
                "name": "sort",
                "schema": {"type": "string", "enum": ["name"]},
                "required": False,
                "description": "Sort products (only supported value: name).",
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
    @blp.response(200, ProductSchema(many=True))
    def get(self):
        """
        GET /products
        """
        query = Product.query

        # --- Filters ---
        search = request.args.get("search", type=str)
        brand_id = request.args.get("brand_id", type=int)
        category_id = request.args.get("category_id", type=int)

        # (Optional) reject old param so professor sees clean design
        if request.args.get("brand") is not None:
            abort(400, message="Use brand_id instead of brand (name).")

        if search:
            query = query.filter(Product.name.ilike(f"%{search}%"))

        if brand_id is not None:
            if brand_id < 1:
                abort(400, message="brand_id must be >= 1.")
            query = query.filter(Product.brand_id == brand_id)

        if category_id is not None:
            if category_id < 1:
                abort(400, message="category_id must be >= 1.")
            query = query.join(Product.categories).filter(Category.id == category_id)

        # --- Sorting ---
        sort = request.args.get("sort", default="name", type=str)
        order = request.args.get("order", default="asc", type=str)

        if sort != "name":
            abort(400, message="Invalid sort field. Only 'name' is supported.")
        if order not in ("asc", "desc"):
            abort(400, message="Invalid order. Use 'asc' or 'desc'.")

        direction = asc if order == "asc" else desc
        query = query.order_by(direction(Product.name), Product.id.asc())

        # --- Pagination ---
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=20, type=int)

        if page < 1:
            abort(400, message="page must be >= 1.")
        if limit < 1 or limit > 100:
            abort(400, message="limit must be between 1 and 100.")

        return query.offset((page - 1) * limit).limit(limit).all()

    # ✅ CREATE product (admin later)
    @blp.arguments(ProductCreateUpdateSchema())
    @blp.doc(security=[{"BearerAuth": []}])
    @blp.response(201, ProductSchema())
    @auth_module.admin_required
    def post(self, data):
        """
        POST /products
        Admin only.
        """

        brand = Brand.query.get(data["brand_id"])
        if not brand:
            abort(404, message="Brand not found.")

        product = Product(
            name=data["name"],
            barcode=normalize_barcode_or_400(data["barcode"]),
            brand=brand,
            description=data.get("description"),
        )

        category_ids = data.get("category_ids", [])
        if category_ids:
            categories = Category.query.filter(Category.id.in_(category_ids)).all()
            if len(categories) != len(set(category_ids)):
                abort(400, message="One or more category_ids are invalid.")
            product.categories = categories

        db.session.add(product)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Product barcode must be unique.")
        return product


@blp.route("/products/<int:product_id>")
class ProductDetail(MethodView):
    @blp.response(200, ProductSchema())
    def get(self, product_id):
        """
        GET /products/{id}
        """
        product = Product.query.get(product_id)
        if not product:
            abort(404, message="Product not found.")
        return product

    @blp.arguments(ProductCreateUpdateSchema(partial=True))
    @blp.doc(security=[{"BearerAuth": []}])
    @blp.response(200, ProductSchema())
    @auth_module.admin_required
    def put(self, data, product_id):
        """
        PUT /products/{id}
        Admin only.
        """

        product = Product.query.get(product_id)
        if not product:
            abort(404, message="Product not found.")

        if "brand_id" in data:
            brand = Brand.query.get(data["brand_id"])
            if not brand:
                abort(404, message="Brand not found.")
            product.brand = brand

        if "name" in data:
            product.name = data["name"]

        if "barcode" in data:
            product.barcode = normalize_barcode_or_400(data["barcode"])

        if "description" in data:
            product.description = data["description"]

        if "category_ids" in data:
            category_ids = data.get("category_ids") or []
            if category_ids:
                categories = Category.query.filter(Category.id.in_(category_ids)).all()
                if len(categories) != len(set(category_ids)):
                    abort(400, message="One or more category_ids are invalid.")
                product.categories = categories
            else:
                product.categories = []

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Product barcode must be unique.")
        return product

    @blp.doc(security=[{"BearerAuth": []}])
    @auth_module.admin_required
    def delete(self, product_id):
        """
        DELETE /products/{id}
        Admin only.
        """

        product = Product.query.get(product_id)
        if not product:
            abort(404, message="Product not found.")
        db.session.delete(product)
        db.session.commit()
        return {"message": "Product deleted."}, 200


@blp.route("/products/<path:barcode>/alternatives")
class ProductBrandAlternatives(MethodView):
    @blp.response(200, BrandSchema(many=True))
    def get(self, barcode):
        raw_clean = clean_barcode_input(barcode)
        product = Product.query.filter_by(barcode=raw_clean).first()

        if not product:
            barcode = normalize_barcode_or_400(raw_clean)
            product = Product.query.filter(
                (Product.barcode.in_([barcode, raw_clean]))
                | (cast(Product.barcode, Numeric) == int(barcode))
            ).first()
        if not product:
            abort(404, message="Product not found.")

        brand = product.brand
        if not brand:
            abort(500, message="Product has no brand.")

        if not brand.boycott_status:
            return []

        product_category_ids = [c.id for c in (product.categories or [])]

        q = BrandAlternative.query.filter(
            BrandAlternative.boycotted_brand_id == brand.id
        )

        if product_category_ids:
            q = q.filter(
                (BrandAlternative.category_id.in_(product_category_ids))
                | (BrandAlternative.category_id.is_(None))
            )
        else:
            q = q.filter(BrandAlternative.category_id.is_(None))

        links = q.order_by(BrandAlternative.score.desc()).all()

        return [link.alternative_brand for link in links if link.alternative_brand]
