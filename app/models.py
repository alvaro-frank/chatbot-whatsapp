from datetime import datetime
from .extensions import db

class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'

    id = db.Column(db.Integer, primary_key=True)
    wa_id = db.Column(db.String(50), nullable=False)   # ID do WhatsApp do cliente
    customer_name = db.Column(db.String(100), nullable=False) # Nome do cliente
    
    intent = db.Column(db.String(50), nullable=False)  # Ex: 'alterar_nif'
    user_input = db.Column(db.Text)
    field_value = db.Column(db.String(255))            # O novo NIF (ex: '123456789')
    generated_response = db.Column(db.Text)
    
    status = db.Column(db.String(20), default='PENDING') # PENDING, APPROVED, REJECTED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<ServiceRequest {self.id} - {self.status}>'