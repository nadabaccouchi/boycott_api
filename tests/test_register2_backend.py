import uuid

import pytest

from app import create_app
from db import db


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-secret",
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_unique_user(client):
    unique = uuid.uuid4().hex[:8]
    email = f"user{unique}@test.com"
    response = client.post(
        "/auth/register",
        json={
            "username": f"user{unique}",
            "email": email,
            "password": "password123",
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["user"]["email"] == email
