# ==============================================================================
# FILE: app/repositories/request_repository.py
# DESCRIPTION: Handles all direct database interactions for ServiceRequests.
#              Abstracts SQLAlchemy queries from the business logic layer.
# ==============================================================================

from datetime import datetime
from app.extensions import db
from app.models import ServiceRequest

class RequestRepository:
    """
    Repository class to encapsulate data access logic for ServiceRequest models.
    """

    def get_by_id(self, request_id: int) -> ServiceRequest:
        """
        Fetches a single request by its primary key.
        
        Args:
            request_id (int): The ID of the request.
            
        Returns:
            ServiceRequest: The found object or 404 error if not found.
        """
        return ServiceRequest.query.get_or_404(request_id)

    def get_all_pending(self) -> list[ServiceRequest]:
        """
        Retrieves all ServiceRequests with 'PENDING' status.
        
        Returns:
            list[ServiceRequest]: A list of pending requests.
        """
        return ServiceRequest.query.filter_by(status='PENDING').all()

    def save(self):
        """
        Commits current session changes to the database.
        """
        db.session.commit()

    def add(self, request: ServiceRequest):
        """
        Adds a new request to the session and commits.
        
        Args:
            request (ServiceRequest): The new request object.
        """
        db.session.add(request)
        db.session.commit()