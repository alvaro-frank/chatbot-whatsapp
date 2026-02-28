import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict

class RequestStatus(Enum):
    """
    Represents the possible states of a customer request in the lifecycle.
    
    Attributes:
        PENDING: Request is awaiting review.
        APPROVED: Request has been accepted and processed.
        REJECTED: Request has been declined.
    """
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
        simulation_data (Dict): Results from the simulation command.
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
    simulation_data: Optional[Dict] = None
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    
    def approve(self):
        """
        Transition the request status to APPROVED.
        
        Sets the processed_at timestamp to the current UTC time.
        
        Raises:
            ValueError: If the request is not currently in PENDING status.
        """
        if self.status != RequestStatus.PENDING:
            raise ValueError(f"Approve Request Error: Request is already {self.status.name}.")
        
        self.status = RequestStatus.APPROVED
        self.processed_at = datetime.now(timezone.utc)
    
    def reject(self):
        """
        Transition the request status to REJECTED.
        
        Sets the processed_at timestamp to the current UTC time.
        
        Raises:
            ValueError: If the request is not currently in PENDING status.
        """
        if self.status != RequestStatus.PENDING:
            raise ValueError(f"Reject Request Error: Request is already {self.status.name}.")
        
        self.status = RequestStatus.REJECTED
        self.processed_at = datetime.now(timezone.utc)
        
@dataclass(frozen=True)
class MessageAnalysis:
    """
    Structured results from the Natural Language Understanding (NLU) processing.
    
    Attributes:
        detected_language (str): The ISO language code detected in the message.
        intent (str): The classified purpose of the customer's message.
        field_value (Optional[str]): The specific data point (e.g., a date or email) extracted.
        confidence_score (float): The AI's confidence level in the analysis (0.0 to 1.0).
        response_draft (str): A suggested response generated for the customer.
    """
    detected_language: str
    intent: str
    field_value: Optional[str]
    confidence_score: float
    response_draft: str
    
@dataclass(frozen=True)
class ReceivedMessage:
    """
    Represents an incoming message payload from a messaging platform.
    
    Attributes:
        sender_id (str): The unique platform identifier for the sender (e.g., phone number).
        sender_name (str): The display name of the sender.
        content (str): The raw text content of the message.
    """
    sender_id: str
    sender_name: str
    content: str

    @property
    def first_name(self) -> str:
        """
        Helper property to extract the first name from the sender_name.
        
        Returns:
            str: The first segment of the name, or an empty string if sender_name is empty.
        """
        return self.sender_name.split()[0] if self.sender_name else ""