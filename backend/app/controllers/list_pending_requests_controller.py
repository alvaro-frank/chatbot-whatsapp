# backend/app/infrastructure/controllers/requests_query_controller.py
import logging
from flask import Blueprint, jsonify
from app.application.use_cases.list_pending_requests import ListPendingRequestsUseCase

pending_requests_blueprint = Blueprint("requests_query", __name__, url_prefix="/admin/requests")

class ListPendingRequestsController:
    """
    Controller responsible for handling administrative queries regarding pending requests.
    
    This class orchestrates the flow between the HTTP delivery mechanism and the 
    underlying business logic for retrieving simulation/request data.
    """
    def __init__(self, list_use_case: ListPendingRequestsUseCase):
        """
        Initializes the controller with the necessary use case.

        Args:
            list_use_case (ListPendingRequestsUseCase): The application service 
                responsible for retrieving pending request records.
        """
        self.list_use_case = list_use_case

    def list_requests(self):
        """
        Endpoint handler to retrieve all pending requests.

        Executes the business logic via the use case, transforms the resulting 
        DTOs (Data Transfer Objects) into JSON, and handles potential 
        infrastructure or application-level errors.

        Returns:
            tuple: A JSON list of requests and the corresponding HTTP status code.
        """
        try:
            requests_dtos = self.list_use_case.execute()
            return jsonify([r.model_dump() for r in requests_dtos]), 200
        except Exception as e:
            logging.error(f"Listing Requests error: {e}", exc_info=True)
            return jsonify({"error": "Dashboard loading error"}), 500

def register_pending_requests_routes(list_uc):
    """
    Factory function to initialize the controller and register its routes 
    within the Flask Blueprint.

    Args:
        list_uc (ListPendingRequestsUseCase): The injected use case dependency.

    Returns:
        Blueprint: The configured Flask blueprint for requests query.
    """
    controller = ListPendingRequestsController(list_uc)
    pending_requests_blueprint.add_url_rule("/", "list_requests", controller.list_requests, methods=["GET"])
    return pending_requests_blueprint