# ==============================================================================
# FILE: app/domain/models.py
# DESCRIPTION: Database Schema definitions (SQLAlchemy Models).
#              Defines the structure of the 'ServiceRequest' entity.
# ==============================================================================

from datetime import datetime
from app.infrastructure.database import db

class ServiceRequest(db.Model):
    """
    Represents a customer request received via WhatsApp.
    Managed by RequestRepository.
    """
    __tablename__ = 'service_requests'

    id = db.Column(db.Integer, primary_key=True)
    wa_id = db.Column(db.String(50), nullable=False) # WhatsApp ID (Phone)
    customer_name = db.Column(db.String(100), nullable=False) # Nome do cliente
    
    intent = db.Column(db.String(50), nullable=False)  # Intent identified by AI
    user_input = db.Column(db.Text) # Raw message from user
    field_value = db.Column(db.String(255)) # Value to be changed       
    generated_response = db.Column(db.Text) # Draft response from AI
    
    status = db.Column(db.String(20), default='PENDING') # PENDING, APPROVED, REJECTED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<ServiceRequest {self.id} - {self.status}>'