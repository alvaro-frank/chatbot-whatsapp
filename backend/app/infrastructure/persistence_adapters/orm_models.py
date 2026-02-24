from datetime import datetime
from app.infrastructure.database import db

class RequestORM(db.Model):
    """
    Represents a customer request received via WhatsApp.
    Managed by RequestRepository.
    """
    __tablename__ = 'requests'

    uid = db.Column(db.String(36), primary_key=True)
    wa_id = db.Column(db.String(50), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    
    intent = db.Column(db.String(50))
    user_input = db.Column(db.Text)
    field_value = db.Column(db.String(255))
    generated_response = db.Column(db.Text)
    
    status = db.Column(db.String(20), nullable=False)
    
    created_at = db.Column(db.DateTime, nullable=False)
    processed_at = db.Column(db.DateTime, nullable=True)