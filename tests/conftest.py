import pytest
from app import create_app
from app.extensions import db
from sqlalchemy.pool import StaticPool

@pytest.fixture(scope='session')
def app():
    _app = create_app()
    _app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_ENGINE_OPTIONS": {"poolclass": StaticPool},
        "GROQ_API_KEY": "test_key",
        "WEBHOOK_VERIFY_TOKEN": "token_teste"
    })
    return _app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.rollback()
        db.drop_all()
        db.session.remove()