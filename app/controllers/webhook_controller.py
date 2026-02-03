# ==============================================================================
# FILE: app/controllers/webhook_controller.py
# DESCRIPTION: Controller layer for WhatsApp Webhook.
#              Handles verification (GET) and event reception (POST).
# ==============================================================================

import logging
from flask import Blueprint, request, jsonify, current_app, make_response
from app.decorators.security import signature_required
from app.repositories.request_repository import RequestRepository
from app.services.whatsapp_service import WhatsAppService
from app.services.ai_service import AIService
from app.utils.whatsapp_parser import parse_whatsapp_message

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook", methods=["GET"])
def verify_webhook():
    """
    Handles the verification challenge from Meta/Facebook.
    Used when setting up the webhook in the Developer Portal.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == current_app.config["VERIFY_TOKEN"]:
            logging.info("✅ WEBHOOK_VERIFIED")

            return make_response(challenge, 200)
        else:
            logging.warning("❌ VERIFICATION_FAILED: Token mismatch")
            
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400


@webhook_bp.route("/webhook", methods=["POST"])
@signature_required
def handle_incoming_event():
    """
    Receives the event payload from WhatsApp.
    Delegates processing to WhatsAppService.
    """
    body = request.get_json()

    try:
        changes = body.get("entry", [{}])[0].get("changes", [{}])[0]
        if "statuses" in changes.get("value", {}):
            return jsonify({"status": "ok"}), 200
    except IndexError:
        pass

    try:
        # 1. Parse JSON to DTO
        message_dto = parse_whatsapp_message(body)
        
        # 2. Dependency Injection
        repo = RequestRepository()
        ai_service = AIService()
        service = WhatsAppService(repo=repo, ai_service=ai_service)
        
        # 3. Process
        service.process_incoming_message(message_dto)
        
    except ValueError as e:
        logging.warning(f"Ignored event: {e}")
    except Exception as e:
        logging.error(f"Error in webhook: {e}")

    return jsonify({"status": "ok"}), 200