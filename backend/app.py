import os

from flask import Flask, jsonify, send_from_directory
from flask_smorest import Api
from werkzeug.exceptions import HTTPException

from config import Config
from db import db

# Import all models so SQLAlchemy recognizes them
from models.user import User
from models.report import Report
from models.product import Product
from models.brand import Brand
from models.category import Category
from models.brand_alternative import BrandAlternative

from resources.auth import blp as auth_blp
from resources.barcode import blp as barcode_blp
from resources.categories import blp as categories_blp
from resources.brands import blp as brands_blp
from resources.products import blp as products_blp
from resources.reports import blp as reports_blp
# from resources.search import blp as search_blp  # (you said you'll delete it)


def custom_schema_name_resolver(schema):
    """Resolver that includes instance context to make schema names unique"""
    # For partial schemas, add suffix
    if hasattr(schema, 'partial') and schema.partial:
        return f"{schema.__class__.__name__}Partial"
    return schema.__class__.__name__


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        # consistent format for abort(400/404/...)
        return jsonify({
            "status": "error",
            "code": e.code,
            "message": e.description,
        }), e.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(e: Exception):
        # Log the full error for debugging
        import traceback
        traceback.print_exc()
        # consistent format for unexpected crashes
        return jsonify({
            "status": "error",
            "code": 500,
            "message": "Internal server error",
        }), 500


def create_app():
    frontend_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend")
    )
    app = Flask(__name__, static_folder=frontend_path, static_url_path="/static")
    app.config.from_object(Config)
    # ✅ Add this one line
    register_error_handlers(app)

    db.init_app(app)
    api = Api(app)
    
    # Add security scheme for Bearer token
    api.spec.components.security_scheme("BearerAuth", {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT token for authentication"
    })
    
    # Apply custom schema name resolver to the MarshmallowPlugin
    # that flask-smorest created
    for plugin in api.spec.plugins:
        if hasattr(plugin, 'converter') and hasattr(plugin.converter, 'schema_name_resolver'):
            plugin.converter.schema_name_resolver = custom_schema_name_resolver
    
    api.register_blueprint(auth_blp)
    api.register_blueprint(barcode_blp)
    api.register_blueprint(categories_blp)
    api.register_blueprint(brands_blp)
    api.register_blueprint(products_blp)
    api.register_blueprint(reports_blp)
    # api.register_blueprint(search_blp)  # (delete if endpoint removed)

    @app.get("/")
    def home():
        return send_from_directory(frontend_path, "index.html")

    @app.get("/health")
    def health():
        return {"message": "Boycott API Running!"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
