import logging
from flask import Blueprint, request, jsonify, current_app
from app.decorators.security import signature_required
# Mappers
from app.infrastructure.mappers import map_whatsapp_json_to_dto
# Domain
from app.domain.entities import ReceivedMessage
# Use Cases
from app.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
# Adapters 
from app.infrastructure.web_adapters.groq_adapter import GroqAdapter
from app.infrastructure.web_adapters.meta_whatsapp_adapter import MetaWhatsAppAdapter
from app.infrastructure.persistence_adapters.request_repository import RequestRepository

webhook_blueprint = Blueprint("webhook", __name__)

@webhook_blueprint.route("/webhook", methods=["GET"])
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

@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def handle_webhook():
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

        repo = RequestRepository()
        llm_provider = GroqAdapter(api_key=current_app.config["GROQ_API_KEY"])
        
        use_case = ProcessIncomingMessageUseCase(
            llm_provider=llm_provider, 
            repo=repo
        )
        
        use_case.execute(domain_message)
        
    except Exception as e:
        logging.error(f"Error handling webhook: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 200

    return jsonify({"status": "ok"}), 200