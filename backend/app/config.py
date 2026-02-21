# ==============================================================================
# FILE: app/config.py
# DESCRIPTION: Application configuration management.
#              Loads environment variables and sets Flask app settings.
# ==============================================================================

import sys
import os
from dotenv import load_dotenv
import logging

def load_configurations(app):
    """
    Loads environment variables from .env file into the Flask app config.
    """
    load_dotenv()
    
    # Meta / WhatsApp API
    app.config["ACCESS_TOKEN"] = os.getenv("ACCESS_TOKEN")
    app.config["YOUR_PHONE_NUMBER"] = os.getenv("YOUR_PHONE_NUMBER")
    app.config["APP_ID"] = os.getenv("APP_ID")
    app.config["APP_SECRET"] = os.getenv("APP_SECRET")
    app.config["RECIPIENT_WAID"] = os.getenv("RECIPIENT_WAID")
    app.config["VERSION"] = os.getenv("VERSION")
    app.config["PHONE_NUMBER_ID"] = os.getenv("PHONE_NUMBER_ID")
    app.config["VERIFY_TOKEN"] = os.getenv("VERIFY_TOKEN")
    
    # AI / LLM
    app.config["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    
    # Database
    basedir = os.path.abspath(os.path.dirname(__file__)) # pasta app/
    instance_path = os.path.join(os.path.dirname(basedir), 'instance')
    db_path = os.path.join(instance_path, 'chatbot.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def configure_logging():
    """
    Sets up the logging format and level (INFO).
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
