from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class IncomingMessageCommand(BaseModel):
    """
    Data Transfer Object representing a validated incoming WhatsApp message.

    Attributes:
        wa_id (str): The unique WhatsApp identifier (usually the phone number) of the sender.
        sender_name (str): The display name or profile name provided by the messaging platform.
        message_body (str): The raw text content of the received message.
    """
    model_config = ConfigDict(frozen=True)

    wa_id: str = Field(..., description="WhatsApp ID of the sender")
    sender_name: str = Field(..., description="Full name of the sender")
    message_body: str = Field(..., description="Content of the message sent")
    
class ManageRequestCommand(BaseModel):
    """
    Data Transfer Object representing a validated managed Request.

    Attributes:
        request_id (str): The unique identifier of the managed Request.
        override_text (str): The generated text by the outgoing adapter to possibly be overrided 
    """
    request_id: str
    override_text: Optional[str] = None