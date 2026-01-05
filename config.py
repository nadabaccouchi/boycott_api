import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "sqlite:///boycott.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
