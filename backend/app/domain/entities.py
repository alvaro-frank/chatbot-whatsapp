import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

class RequestStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

@dataclass
class Request:
    """
    Represents the created customer request
    
    Attributes:
        wa_id (str): Whatsapp ID
        customer_name (str): Customer Name
        intent (str): the customer's intent
        user_input (str): the customer's message
        field_value (str): the new value for update
        generated_response (str): the response sent to the customer
        status (str): status of the request (PENDING, APPROVED, REJECTED)
        created_at (datetime): creation date of the request
        processed_at (datetime): processed date of the request
    """
    wa_id: str
    customer_name: str
    intent: str
    user_input: str
    field_value: str        
    generated_response: str
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    
    def approve(self):
        if self.status != RequestStatus.PENDING:
            raise ValueError(f"Approve Request Error: Request is already {self.status.name}.")
        
        self.status = RequestStatus.APPROVED
        self.processed_at = datetime.now(timezone.utc)
    
    def reject(self):
        if self.status != RequestStatus.PENDING:
            raise ValueError(f"Reject Request Error: Request is already {self.status.name}.")
        
        self.status = RequestStatus.REJECTED
        self.processed_at = datetime.now(timezone.utc)