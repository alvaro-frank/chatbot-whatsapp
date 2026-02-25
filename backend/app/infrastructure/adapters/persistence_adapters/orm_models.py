from datetime import datetime
from app.infrastructure.database import db

class RequestORM(db.Model):
    """
    SQLAlchemy ORM model representing a customer request in the database.
    
    This class maps the domain 'Request' entity to the 'requests' table, 
    persisting message history, AI analysis, and processing timestamps.

    Attributes:
        uid (str): Primary key using a UUID string (36 characters).
        wa_id (str): The sender's WhatsApp identifier (phone number).
        customer_name (str): The name associated with the WhatsApp profile.
        intent (str): The business action identified by the AI (e.g., 'update_info').
        user_input (str): The raw text of the message received from the customer.
        field_value (str): The specific piece of data extracted for the update.
        generated_response (str): The draft or final response text prepared for the user.
        status (str): The current lifecycle state (PENDING, APPROVED, REJECTED).
        simulation_data (JSON): Persisted results from the simulation command.
        created_at (datetime): Timestamp of when the record was first inserted.
        processed_at (Optional[datetime]): Timestamp of when the status was last updated.
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
    simulation_data = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, nullable=False)
    processed_at = db.Column(db.DateTime, nullable=True)