import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url

from config import Config


def get_test_db_url() -> str:
    env_url = os.getenv("TEST_DATABASE_URL")
    if env_url:
        return env_url
    base_url = make_url(Config.SQLALCHEMY_DATABASE_URI)
    if not base_url.database:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is missing a database name.")
    db_name = base_url.database
    if not db_name.lower().endswith("_test"):
        db_name = f"{db_name}_test"
    return str(base_url.set(database=db_name))


def ensure_test_db():
    test_url = make_url(get_test_db_url())
    admin_url = test_url.set(database="postgres")

    engine = create_engine(admin_url)
    db_name = test_url.database

    with engine.connect() as conn:
        conn = conn.execution_options(isolation_level="AUTOCOMMIT")
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).scalar()
        if exists:
            print(f"Test database already exists: {db_name}")
            return
        conn.execute(text(f'CREATE DATABASE "{db_name}"'))
        print(f"Test database created: {db_name}")


if __name__ == "__main__":
    ensure_test_db()
