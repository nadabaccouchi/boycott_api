from flask import Flask
from config import Config
from resources.barcode import blp as barcode_blp  # Relative import
from resources.brands import blp as brands_blp    # Relative import
from resources.categories import blp as categories_blp  # Relative import
from resources.products import blp as products_blp  # Relative import
from resources.search import blp as search_blp    # Relative import
from db import db  # Import db instance
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

# Initialize db and migration
db.init_app(app)
migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(barcode_blp)
app.register_blueprint(brands_blp)
app.register_blueprint(categories_blp)
app.register_blueprint(products_blp)
app.register_blueprint(search_blp)

@app.route('/')
def hello_world():
    return 'Boycott API Running!'

if __name__ == '__main__':
    app.run(debug=True)
