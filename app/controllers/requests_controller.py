# ==============================================================================
# FILE: app/controllers/requests_controller.py
# DESCRIPTION: Controller layer for handling ServiceRequest endpoints.
#              Receives HTTP inputs, delegates to RequestService, and returns JSON.
# ==============================================================================

from flask import Blueprint, jsonify, request
from app.services.request_service import RequestService

requests_bp = Blueprint("requests_controller", __name__, url_prefix="/admin/requests")

repo = RequestRepository()
service = RequestService(repo=repo)

@requests_bp.route("/", methods=["GET"])
def get_pending_requests():
    """
    Endpoint to fetch pending requests. 
    Triggers automatic cleanup via the service layer.
    """
    try:
        data = service.list_active_requests()
        return jsonify(data), 200
    except Exception as e:
        print(f"Error fetching requests: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@requests_bp.route("/<int:request_id>/approve", methods=["POST"])
def approve_request(request_id):
    """
    Endpoint to approve a specific request.
    """
    try:
        body = request.get_json(silent=True) or {}
        custom_text = body.get('response_text')
        
        service.process_approval(request_id, custom_text)
        return jsonify({"message": "Aprovado e enviado com sucesso!"}), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error approving: {e}")
        return jsonify({"error": "Falha ao processar aprovação"}), 500

@requests_bp.route("/<int:request_id>/reject", methods=["POST"])
def reject_request(request_id):
    """
    Endpoint to reject a specific request.
    """
    try:
        body = request.get_json(silent=True) or {}
        custom_text = body.get('response_text')
        
        service.process_rejection(request_id, custom_text)
        return jsonify({"message": "Pedido rejeitado e cliente notificado."}), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Error rejecting: {e}")
        return jsonify({"error": "Falha ao processar rejeição"}), 500