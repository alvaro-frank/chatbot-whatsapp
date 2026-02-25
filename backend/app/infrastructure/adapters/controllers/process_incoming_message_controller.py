import logging
from flask import Blueprint, request, jsonify, current_app
from app.infrastructure.middleware.security import signature_required
# Mappers
from app.infrastructure.mappers.whatsapp_json_dto_mapper import map_whatsapp_json_to_dto
# Domain
from app.domain.entities import ReceivedMessage
# Use Cases
from app.application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase

incoming_message_blueprint = Blueprint("webhook", __name__)

class ProcessIncomingMessageController:
    """
    Controller for handling incoming communication from the WhatsApp Business API.
    
    This class manages the lifecycle of a webhook request, including the initial 
    verification handshake and the asynchronous processing of user messages.
    """
    def __init__(self, use_case: ProcessIncomingMessageUseCase):
        """
        Initializes the controller with the message processing use case.

        Args:
            use_case (ProcessIncomingMessageUseCase): The application service 
                that orchestrates AI interaction and system state changes.
        """
        self.use_case = use_case
        
    def verify_webhook():
        """
        Handles Meta's Webhook verification challenge (Handshake).
        
        Meta sends a GET request with a hub.verify_token to ensure the 
        endpoint is valid and owned by the developer. This is only required 
        during the initial setup or configuration changes in the Meta Dashboard.
        
        Returns:
            tuple: (challenge string, status code) if verified, 
                otherwise error JSON and 403.
        """
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        
        logging.error("VERIFICATION_FAILED")
        return jsonify({"status": "error", "message": "Verification failed"}), 403

    @signature_required
    def handle_webhook(self):
        """
        Main entry point for incoming WhatsApp messages and notifications.
        
        This endpoint is protected by the @signature_required decorator to ensure 
        request authenticity. It maps the complex Meta JSON to a DTO, converts it 
        to a Domain Entity, and triggers the message processing Use Case.

        Returns:
            tuple: JSON status and HTTP 200 (Meta requires a 200 OK even if 
                processing fails internally to stop retries).
        """
        body = request.get_json()
        
        try:
            message_dto = map_whatsapp_json_to_dto(body)
            if not message_dto:
                return jsonify({"status": "ignored"}), 200

            domain_message = ReceivedMessage(
                sender_id=message_dto.wa_id,
                sender_name=message_dto.sender_name,
                content=message_dto.message_body
            )
            
            self.use_case.execute(domain_message)
            
        except Exception as e:
            logging.error(f"Error handling webhook: {e}", exc_info=True)
            return jsonify({"status": "error", "message": str(e)}), 200

        return jsonify({"status": "ok"}), 200

def incoming_message_routes(process_use_case):
    """
    Factory to initialize the controller and register the Webhook routes.

    Args:
        process_use_case (ProcessIncomingMessageUseCase): The injected use case.

    Returns:
        Blueprint: The configured Flask blueprint for incoming messages.
    """
    controller = ProcessIncomingMessageController(process_use_case)
    
    incoming_message_blueprint.add_url_rule(
        "/webhook", 
        view_func=controller.verify_webhook, 
        methods=["GET"]
    )
    incoming_message_blueprint.add_url_rule(
        "/webhook", 
        view_func=controller.handle_webhook, 
        methods=["POST"]
    )
    
    return incoming_message_blueprint