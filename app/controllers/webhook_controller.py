# ==============================================================================
# FILE: app/controllers/webhook_controller.py
# DESCRIPTION: Entry point for Meta's WhatsApp Webhook events.
#              Handles security handshakes (GET) and incoming messaging 
#              orchestration (POST). Ensures all raw payloads are parsed into 
#              typed DTOs before entering the domain layer.
# ==============================================================================

import logging
from flask import Blueprint, request, jsonify, current_app
from app.decorators.security import signature_required
from app.utils.whatsapp_parser import parse_whatsapp_message
from app.dtos.dtos import IncomingMessageDTO
from app.infrastructure.groq_adapter import GroqAdapter
from app.infrastructure.meta_whatsapp_adapter import MetaWhatsAppAdapter
from app.repositories.request_repository import RequestRepository
from app.services.request_service import RequestService
from app.services.whatsapp_service import WhatsAppService

webhook_blueprint = Blueprint("webhook", __name__)

@webhook_blueprint.route("/webhook", methods=["GET"])
def verify_webhook():
    """
    Handles Meta's Webhook verification challenge (Handshake).
    
    Meta sends a GET request with a hub.verify_token to ensure the 
    endpoint is valid and owned by the developer.
    
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
    Processes incoming WhatsApp events (messages, statuses, etc.).
    
    This method acts as a Factory/Assembler, manually injecting 
    dependencies into the Service layer. It transforms raw JSON 
    payloads into structured IncomingMessageDTOs.
    
    Logic Flow:
    1. Parse JSON into DTO.
    2. Instantiate Repository and Infrastructure Adapters.
    3. Assemble Domain Services via Dependency Injection.
    4. Execute business orchestration.

    Returns:
        JSON: Standard 200 OK response required by Meta to avoid retries.
    """
    body = request.get_json()
    try:
        message_dto = parse_whatsapp_message(body)
        
        repo = RequestRepository()
        
        llm_provider = GroqAdapter(api_key=current_app.config["GROQ_API_KEY"])
        whatsapp_provider = MetaWhatsAppAdapter(
            token=current_app.config["ACCESS_TOKEN"],
            phone_number_id=current_app.config["PHONE_NUMBER_ID"]
        )
        
        req_service = RequestService(repo=repo, whatsapp_provider=whatsapp_provider)
        service = WhatsAppService(
            llm_provider=llm_provider, 
            whatsapp_provider=whatsapp_provider,
            request_service=req_service
        )
        
        service.process_incoming_message(message_dto)
        
    except Exception as e:
        logging.error(f"Error processing Webhook: {e}")

    return jsonify({"status": "ok"}), 200