from flask import Flask
from flask_cors import CORS
from app.config import load_configurations, configure_logging
from app.infrastructure.database import db
import os
from app.controllers.manage_request_action_controller import register_manage_requests_routes
from app.controllers.list_pending_requests_controller import register_pending_requests_routes
from app.controllers.process_incoming_message_controller import incoming_message_routes
from app.infrastructure.adapters.persistence_adapters.request_repository import RequestRepository
from app.infrastructure.adapters.web_adapters.meta_whatsapp_adapter import MetaWhatsAppAdapter
from app.application.use_cases.list_pending_requests import ListPendingRequestsUseCase
from app.application.use_cases.manage_request_action import ManageRequestActionUseCase
from app.infrastructure.adapters.web_adapters.groq_adapter import GroqAdapter
from app.application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    load_configurations(app)
    configure_logging()
    
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if db_uri and db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

    CORS(app)

    db.init_app(app)

    with app.app_context(): 
        # Outgoing Adapters
        repo = RequestRepository()
        whatsapp = MetaWhatsAppAdapter(
            token=app.config["ACCESS_TOKEN"],
            phone_number_id=app.config["PHONE_NUMBER_ID"]
        )
        groq = GroqAdapter(api_key=app.config["GROQ_API_KEY"])

        # 2. Use Cases
        list_uc = ListPendingRequestsUseCase(repo=repo)
        manage_uc = ManageRequestActionUseCase(repo=repo, whatsapp_provider=whatsapp)
        process_uc = ProcessIncomingMessageUseCase(
            repo=repo, 
            llm_provider=groq
        )
        
        # 3. Ingoing Adapters (Controllers)
        pending_requests_bp = register_pending_requests_routes(list_uc)
        manage_requests_bp = register_manage_requests_routes(manage_uc)
        incoming_message_bp = incoming_message_routes(process_uc)
        
        app.register_blueprint(pending_requests_bp)
        app.register_blueprint(manage_requests_bp)      
        app.register_blueprint(incoming_message_bp)

        db.create_all()

    return app
