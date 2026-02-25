# backend/app/infrastructure/controllers/requests_query_controller.py
import logging
from flask import Blueprint, jsonify
from app.application.use_cases.list_pending_requests import ListPendingRequestsUseCase

pending_requests_blueprint = Blueprint("requests_query", __name__, url_prefix="/admin/requests")

class ListPendingRequestsController:
    def __init__(self, list_use_case: ListPendingRequestsUseCase):
        self.list_use_case = list_use_case

    def list_requests(self):
        try:
            requests_dtos = self.list_use_case.execute()
            return jsonify([r.model_dump() for r in requests_dtos]), 200
        except Exception as e:
            logging.error(f"Listing Requests error: {e}", exc_info=True)
            return jsonify({"error": "Dashboard loading error"}), 500

def register_pending_requests_routes(list_uc):
    controller = ListPendingRequestsController(list_uc)
    pending_requests_blueprint.add_url_rule("/", "list_requests", controller.list_requests, methods=["GET"])
    return pending_requests_blueprint