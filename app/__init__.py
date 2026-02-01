from flask import Flask
from app.config import load_configurations, configure_logging
from app.controllers.webhook_controller import webhook_bp
from app.controllers.requests_controller import requests_bp
from .extensions import db


def create_app():
    app = Flask(__name__)

    load_configurations(app)
    configure_logging()

    db.init_app(app)

    app.register_blueprint(webhook_bp)
    app.register_blueprint(requests_bp)
    
    with app.app_context():
        db.create_all()

    return app
