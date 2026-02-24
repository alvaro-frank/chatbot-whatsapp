import logging
from flask import Blueprint, request, jsonify, current_app
from app.domain.interfaces import NotificationDeliveryError
# Use Cases
from app.use_cases.list_pending_requests import ListPendingRequestsUseCase
from app.use_cases.manage_request_action import ManageRequestActionUseCase
# Infraestrutura
from app.infrastructure.web_adapters.meta_whatsapp_adapter import MetaWhatsAppAdapter
from app.infrastructure.persistence_adapters.request_repository import RequestRepository

requests_blueprint = Blueprint("requests", __name__, url_prefix="/admin/requests")

def get_list_use_case():
    """
    Dependency Injector for the ListPendingRequestsUseCase.
    
    Returns:
        ListPendingRequestsUseCase: An instance initialized with the RequestRepository.
    """
    return ListPendingRequestsUseCase(repo=RequestRepository())

def get_manage_use_case():
    """
    Dependency Injector for the ManageRequestActionUseCase.
    
    Initializes the WhatsApp adapter using current application configuration 
    (token and phone ID) before injecting it into the management use case.

    Returns:
        ManageRequestActionUseCase: An instance ready to process approvals/rejections.
    """
    whatsapp_provider = MetaWhatsAppAdapter(
        token=current_app.config["ACCESS_TOKEN"],
        phone_number_id=current_app.config["PHONE_NUMBER_ID"]
    )
    return ManageRequestActionUseCase(
        repo=RequestRepository(), 
        whatsapp_provider=whatsapp_provider
    )

@requests_blueprint.route("/", methods=["GET"])
def list_requests():
    """
    Endpoint to retrieve all pending customer requests for the dashboard.
    
    Transforms domain entities into JSON-serializable DTOs.
    
    Returns:
        JSON: A list of pending requests with simulation data.
    """
    try:
        use_case = get_list_use_case()
        requests_dtos = use_case.execute()
        
        return jsonify([r.model_dump() for r in requests_dtos]), 200
    except Exception as e:
        logging.error(f"Listing Requests error: {e}", exc_info=True)
        return jsonify({"error": "Dashboard loading error"}), 500

@requests_blueprint.route("/<string:request_id>/approve", methods=["POST"])
def approve_request(request_id):
    """
    Endpoint to approve a specific request and notify the customer.
    
    Expects an optional 'response_text' in the JSON body to override the 
    AI-generated default message.
    """
    data = request.get_json() or {}
    override_text = data.get("response_text")

    try:
        use_case = get_manage_use_case()
        use_case.approve(request_id, override_text)
        return jsonify({"status": "success", "message": "Request approved successfully"}), 200
        
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except NotificationDeliveryError as e:
        return jsonify({"status": "error", "message": f"Whatsapp Notification Error: {e}"}), 502
    except Exception as e:
        logging.error(f"Erro crítico na aprovação: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Internal Server Error"}), 500

@requests_blueprint.route("/<string:request_id>/reject", methods=["POST"])
def reject_request(request_id):
    """
    Endpoint to reject a specific request and notify the customer.
    
    Updates the request status to REJECTED and dispatches a declination message.
    """
    data = request.get_json() or {}
    override_text = data.get("response_text")

    try:
        use_case = get_manage_use_case()
        use_case.reject(request_id, override_text)
        return jsonify({"status": "success", "message": "Pedido rejeitado"}), 200
        
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except NotificationDeliveryError as e:
        return jsonify({"status": "error", "message": "Não foi possível avisar o cliente da rejeição"}), 502
    except Exception as e:
        logging.error(f"Erro crítico na rejeição: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Erro interno"}), 500