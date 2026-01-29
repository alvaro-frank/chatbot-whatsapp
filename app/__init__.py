from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint
from .extensions import db


def create_app():
    app = Flask(__name__)

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()

    db.init_app(app)

    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)
    
    with app.app_context():
        db.create_all()

    return app
