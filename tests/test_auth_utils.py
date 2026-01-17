import auth_utils as auth_module


def test_create_and_decode_token(app):
    with app.app_context():
        token = auth_module.create_access_token(123, "admin", expires_in=60)
        payload = auth_module.decode_token(token)
        assert payload is not None
        assert payload["user_id"] == 123
        assert payload["user_role"] == "admin"


def test_decode_invalid_token_returns_none(app):
    with app.app_context():
        payload = auth_module.decode_token("not-a-real-token")
        assert payload is None
