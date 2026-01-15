import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Default to sqlite if DATABASE_URL not provided
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///boycott.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Smorest (Swagger/OpenAPI)
    API_TITLE = "Boycott API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
