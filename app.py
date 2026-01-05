from flask import Flask
from flask_smorest import Api
from db import db
import models

from resources.barcode import blp as BarcodeBlueprint
from resources.brands import blp as BrandsBlueprint
from resources.products import blp as ProductsBlueprint
from resources.categories import blp as CategoriesBlueprint
from resources.search import blp as SearchBlueprint

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///boycott.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["API_TITLE"] = "Enhanced Boycott API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

db.init_app(app)
api = Api(app)

# Register all blueprints
api.register_blueprint(BarcodeBlueprint)
api.register_blueprint(BrandsBlueprint)
api.register_blueprint(ProductsBlueprint)
api.register_blueprint(CategoriesBlueprint)
api.register_blueprint(SearchBlueprint)

@app.route("/")
def home():
    return {"message": "Enhanced Boycott API running. Visit /swagger-ui"}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

