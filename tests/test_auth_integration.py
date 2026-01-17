from db import db
from models.user import User


def create_user(email, username, password, role="user"):
    user = User(username=username, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email, password):
    return client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(client):
    register_resp = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
        },
    )
    assert register_resp.status_code == 201
    register_data = register_resp.get_json()
    assert "access_token" in register_data

    login_resp = client.post(
        "/auth/login",
        json={"email": "testuser@example.com", "password": "password123"},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.get_json()
    assert "access_token" in login_data


def test_categories_requires_auth_header(client):
    resp = client.post(
        "/categories",
        json={"name": "Snacks", "slug": "snacks"},
    )
    assert resp.status_code == 401


def test_categories_admin_only(client):
    create_user("admin@example.com", "admin", "Admin123456", role="admin")
    create_user("user@example.com", "user", "password123", role="user")

    admin_login = login(client, "admin@example.com", "Admin123456")
    assert admin_login.status_code == 200
    admin_token = admin_login.get_json()["access_token"]

    user_login = login(client, "user@example.com", "password123")
    assert user_login.status_code == 200
    user_token = user_login.get_json()["access_token"]

    user_resp = client.post(
        "/categories",
        json={"name": "Drinks", "slug": "drinks"},
        headers=auth_header(user_token),
    )
    assert user_resp.status_code == 403

    admin_resp = client.post(
        "/categories",
        json={"name": "Snacks", "slug": "snacks"},
        headers=auth_header(admin_token),
    )
    assert admin_resp.status_code == 201


def test_reports_auth_required(client):
    create_user("reporter@example.com", "reporter", "password123", role="user")
    login_resp = login(client, "reporter@example.com", "password123")
    token = login_resp.get_json()["access_token"]

    no_auth = client.get("/reports")
    assert no_auth.status_code == 401

    with_auth = client.get("/reports", headers=auth_header(token))
    assert with_auth.status_code == 200

    create_resp = client.post(
        "/reports",
        json={
            "barcode": "12345678",
            "message": "This product should be reviewed.",
        },
        headers=auth_header(token),
    )
    assert create_resp.status_code == 201
