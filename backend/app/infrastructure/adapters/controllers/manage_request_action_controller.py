import logging
from flask import Blueprint, request, jsonify
from app.domain.ports import NotificationDeliveryError
# Use Cases
from app.application.use_cases.manage_request_action import ManageRequestActionUseCase

manage_requests_blueprint = Blueprint("requests", __name__, url_prefix="/admin/requests")

class ManageRequestActionController:
    """
    
    """
    def __init__(self, manage_use_case: ManageRequestActionUseCase):
        """
        
        """
        self.manage_use_case = manage_use_case

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
    
def register_manage_requests_routes(manage_uc):
    controller = ManageRequestActionController(manage_uc)
    
    manage_requests_blueprint.add_url_rule("/<string:request_id>/approve", "approve_request", controller.approve_request, methods=["POST"])
    manage_requests_blueprint.add_url_rule("/<string:request_id>/reject", "reject_request", controller.reject_request, methods=["POST"])
    
    return manage_requests_blueprint