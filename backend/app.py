from flask import Flask
from flask_smorest import Api
from flask_migrate import Migrate

from config import Config
from db import db

from resources.barcode import blp as barcode_blp
from resources.brands import blp as brands_blp
from resources.categories import blp as categories_blp
from resources.products import blp as products_blp
from resources.search import blp as search_blp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)

    api = Api(app)
    api.register_blueprint(barcode_blp)
    api.register_blueprint(brands_blp)
    api.register_blueprint(categories_blp)
    api.register_blueprint(products_blp)
    api.register_blueprint(search_blp)

    @app.get("/")
    def home():
        return {"message": "Boycott API Running!"}

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
