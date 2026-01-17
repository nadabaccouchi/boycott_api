# FILE: auth_utils.py

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, g, request
from flask_smorest import abort
from models.user import User


def create_access_token(user_id, user_role, expires_in=86400):
    """
    Create a JWT access token (default 24 hours).
    """
    payload = {
        "user_id": user_id,
        "user_role": user_role,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )

    # ✅ PyJWT may return bytes → convert to str for JSON
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token


def decode_token(token):
    """
    Decode and validate JWT token.
    Returns payload dict or None if invalid.
    """
    try:
        return jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    """
    Extract and validate JWT from Authorization header.
    Returns User object or aborts.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        abort(401, message="Missing Authorization header.")

    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            abort(401, message="Invalid authorization scheme.")
    except ValueError:
        abort(401, message="Invalid authorization header format.")

    payload = decode_token(token)
    if not payload:
        abort(401, message="Invalid or expired token.")

    user = User.query.get(payload.get("user_id"))
    if not user:
        abort(401, message="User not found.")

    return user


def require_admin():
    """
    Ensure the current user is admin.
    """
    user = get_current_user()
    if user.role != "admin":
        abort(403, message="Admin access required.")
    return user


def require_authenticated_user():
    """
    Ensure the current user is authenticated.
    """
    return get_current_user()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        g.current_user = get_current_user()
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if user.role != "admin":
            abort(403, message="Admin access required.")
        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper
