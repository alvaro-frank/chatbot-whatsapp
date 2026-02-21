# ==============================================================================
# FILE: app/controllers/requests_controller.py
# DESCRIPTION: Controller handling administrative Dashboard operations.
#              Orchestrates the lifecycle of ServiceRequests including listing,
#              manual approval, and rejection through the RequestService.
# ==============================================================================

import logging
from flask import Blueprint, request, jsonify, current_app
from app.infrastructure.meta_whatsapp_adapter import MetaWhatsAppAdapter
from app.repositories.request_repository import RequestRepository
from app.services.request_service import RequestService

requests_blueprint = Blueprint("requests", __name__, url_prefix="/admin/requests")

def get_request_service():
    """
    Dependency Injection helper to instantiate the domain service.
    
    Initializes the RequestRepository and MetaWhatsAppAdapter using 
    application-level configurations before injecting them into the Service.
    
    Returns:
        RequestService: An instance of the orchestrated domain service.
    """
    repo = RequestRepository()
    whatsapp_provider = MetaWhatsAppAdapter(
        token=current_app.config["ACCESS_TOKEN"],
        phone_number_id=current_app.config["PHONE_NUMBER_ID"],
        version=current_app.config["VERSION"]
    )
    return RequestService(repo=repo, whatsapp_provider=whatsapp_provider)

@requests_blueprint.route("/", methods=["GET"])
def list_requests():
    """
    Retrieves all pending service requests for Dashboard display.
    
    The service layer handles the mapping from database models to 
    typed DTOs (Data Transfer Objects), ensuring frontend consistency.
    
    Returns:
        JSON: List of serialized ServiceRequestDTOs.
    """
    try:
        service = get_request_service()
        requests_dtos = service.list_active_requests()
        
        return jsonify([r.model_dump() for r in requests_dtos]), 200
    except Exception as e:
        logging.error(f"Error listing Requests: {e}")
        return jsonify({"error": str(e)}), 500

@requests_blueprint.route("/<int:request_id>/approve", methods=["POST"])
def approve_request(request_id):
    """
    Approves a pending request and triggers external notification.
    
    Args:
        request_id (int): Unique identifier of the request.
        
    Body (JSON):
        response_text (optional): Overridden message text for the customer.
        
    Returns:
        JSON: Operation status and confirmation message.
    """
    data = request.get_json() or {}
    override_text = data.get("response_text")

    try:
        service = get_request_service()
        success = service.process_approval(request_id, override_text)
        
        if success:
            return jsonify({"status": "success", "message": "Request approved"}), 200
        return jsonify({"status": "error", "message": "Failed to send notification"}), 400
        
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        logging.error(f"Request Approval Error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

@requests_blueprint.route("/<int:request_id>/reject", methods=["POST"])
def reject_request(request_id):
    """
    Rejects a pending request and updates the audit trail.
    
    Args:
        request_id (int): Unique identifier of the request.
        
    Returns:
        JSON: Operation status.
    """
    data = request.get_json() or {}
    override_text = data.get("response_text")

    try:
        service = get_request_service()
        service.process_rejection(request_id, override_text)
        return jsonify({"status": "success", "message": "Request rejected"}), 200
        
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        logging.error(f"Request Rejection Error: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500