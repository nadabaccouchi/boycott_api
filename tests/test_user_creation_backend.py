import uuid

import pytest

from app import create_app
from db import db
from models.user import User


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


def test_user_creation(app):
    unique = uuid.uuid4().hex[:8]
    with app.app_context():
        user = User(
            username=f"testuser{unique}",
            email=f"test{unique}@example.com",
            role="user",
        )
        user.set_password("testpass123")

        db.session.add(user)
        db.session.commit()

        assert user.id is not None
