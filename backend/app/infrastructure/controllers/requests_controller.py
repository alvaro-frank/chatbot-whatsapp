import logging
from flask import Blueprint, request, jsonify
from app.domain.interfaces import NotificationDeliveryError
# Use Cases
from app.use_cases.list_pending_requests import ListPendingRequestsUseCase
from app.use_cases.manage_request_action import ManageRequestActionUseCase

requests_blueprint = Blueprint("requests", __name__, url_prefix="/admin/requests")

class RequestsController:
    """
    
    """
    def __init__(self, list_use_case: ListPendingRequestsUseCase, manage_use_case: ManageRequestActionUseCase):
        """
        
        """
        self.list_use_case = list_use_case
        self.manage_use_case = manage_use_case

    def list_requests(self):
        """
        Endpoint to retrieve all pending customer requests for the dashboard.
        
        Transforms domain entities into JSON-serializable DTOs.
        
        Returns:
            JSON: A list of pending requests with simulation data.
        """
        try:
            requests_dtos = self.list_use_case.execute()
            return jsonify([r.model_dump() for r in requests_dtos]), 200
        except Exception as e:
            logging.error(f"Listing Requests error: {e}", exc_info=True)
            return jsonify({"error": "Dashboard loading error"}), 500

    def approve_request(self, request_id):
        """
        Endpoint to approve a specific request and notify the customer.
        
        Expects an optional 'response_text' in the JSON body to override the 
        AI-generated default message.
        """
        data = request.get_json() or {}
        override_text = data.get("response_text")

        try:
            self.manage_use_case.approve(request_id, override_text)
            
            return jsonify({"status": "success", "message": "Request approved successfully"}), 200
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400
        except NotificationDeliveryError as e:
            return jsonify({"status": "error", "message": f"Whatsapp Notification Error: {e}"}), 502
        except Exception as e:
            logging.error(f"Erro crítico na aprovação: {e}", exc_info=True)
            return jsonify({"status": "error", "message": "Internal Server Error"}), 500

    def reject_request(self, request_id):
        """
        Endpoint to reject a specific request and notify the customer.
        
        Updates the request status to REJECTED and dispatches a declination message.
        """
        data = request.get_json() or {}
        override_text = data.get("response_text")

        try:
            self.manage_use_case.reject(request_id, override_text)
            
            return jsonify({"status": "success", "message": "Pedido rejeitado"}), 200
            
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400
        except NotificationDeliveryError as e:
            return jsonify({"status": "error", "message": "Não foi possível avisar o cliente da rejeição"}), 502
        except Exception as e:
            logging.error(f"Erro crítico na rejeição: {e}", exc_info=True)
            return jsonify({"status": "error", "message": "Erro interno"}), 500
    
def register_requests_routes(list_uc, manage_uc):
    controller = RequestsController(list_uc, manage_uc)
    
    requests_blueprint.add_url_rule("/", "list_requests", controller.list_requests, methods=["GET"])
    requests_blueprint.add_url_rule("/<string:request_id>/approve", "approve_request", controller.approve_request, methods=["POST"])
    requests_blueprint.add_url_rule("/<string:request_id>/reject", "reject_request", controller.reject_request, methods=["POST"])
    
    return requests_blueprint