# FILE: resources/auth.py

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError

from db import db
from models.user import User
from schema import UserRegisterSchema, UserLoginSchema, AuthResponseSchema
import auth_utils as auth_module

blp = Blueprint("Auth", __name__, description="Authentication endpoints")


@blp.route("/auth/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema())
    @blp.response(201, AuthResponseSchema())
    def post(self, data):
        """Register a new user"""
        # Public access, no role restrictions
        # Check if user exists
        if User.query.filter_by(email=data["email"]).first():
            abort(409, message="Email already registered.")
        if User.query.filter_by(username=data["username"]).first():
            abort(409, message="Username already taken.")

        # Create new user
        user = User(
            username=data["username"],
            email=data["email"],
            role="user",  # Default role
        )
        user.set_password(data["password"])

        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message="Failed to create user.")

        # Generate token
        token = auth_module.create_access_token(user.id, user.role)

        return {
            "access_token": token,
            "user": user.to_dict(),
        }


@blp.route("/auth/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema())
    @blp.response(200, AuthResponseSchema())
    def post(self, data):
        """Login user and return JWT token"""
        # Public access, no role restrictions
        user = User.query.filter_by(email=data["email"]).first()
        if not user or not user.check_password(data["password"]):
            abort(401, message="Invalid email or password.")

        # Generate token
        token = auth_module.create_access_token(user.id, user.role)

        return {
            "access_token": token,
            "user": user.to_dict(),
        }
