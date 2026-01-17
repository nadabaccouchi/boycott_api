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


def test_routes_include_auth_and_reports(app):
    routes = sorted(
        [rule.rule for rule in app.url_map.iter_rules() if "/static" not in rule.rule]
    )
    assert "/auth/login" in routes
    assert "/auth/register" in routes
    assert "/reports" in routes
