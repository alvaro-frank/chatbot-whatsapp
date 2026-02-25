from abc import ABC, abstractmethod
from app.application.dtos.dtos import AIAnalysisDTO
import uuid
from typing import Optional, List
from app.domain.entities import Request, MessageAnalysis

class NotificationDeliveryError(Exception):
    """
    Exception raised when a message fails to reach its destination.
    
    This error typically encapsulates network failures, API rate limits, 
    or authentication issues with external messaging providers.
    """
    pass

class LLMProvider(ABC):
    """
    Contract for Large Language Model (LLM) implementations.
    
    This interface abstracts the intelligence layer. Implementations are 
    responsible for translating unstructured natural language into structured 
    domain insights (Intents, Entities, and Sentiment).
    """

    @abstractmethod
    def analyze_message(self, message_body: str, user_name: str) -> MessageAnalysis:
        """
        Interprets a user message and extracts business-critical information.
        
        Args:
            message_body (str): The raw text content received from the user.
            user_name (str): The name of the sender, used for contextual personalization.
            
        Returns:
            MessageAnalysis: A structured object containing intent, confidence, and drafts.
        """
        pass

class WhatsAppProvider(ABC):
    """
    Contract for Messaging Transport providers.
    
    This interface abstracts the communication layer. It decouples the domain 
    from specific API protocols (like Meta's Graph API), allowing the system 
    to switch providers without affecting business orchestration.
    """

    @abstractmethod
    def send_text_message(self, recipient_id: str, message_text: str) -> None:
        """
        Dispatches a text message to an external recipient.
        
        Args:
            recipient_id (str): The unique platform ID (phone number) of the receiver.
            message_text (str): The body of the message to be delivered.
            
        Raises:
            NotificationDeliveryError: If the provider fails to dispatch the message.
        """
        pass
    
class IRequestRepository(ABC):
    """
    Data Access Interface for Request entities.
    
    This repository acts as an abstraction between the domain layer and the 
    persistence mechanism (SQL, NoSQL, or In-Memory), ensuring the domain 
    remains agnostic of database technologies.
    """
    @abstractmethod
    def get_by_id(self, uid: uuid.UUID) -> Optional[Request]:
        """
        Fetches a single request by its primary key.
        
        Args:
            uid (uuid.UUID): The unique identifier of the request.
            
        Returns:
            Optional[Request]: The Request object if found, otherwise None.
        """
        pass

    @abstractmethod
    def get_all_pending(self) -> List[Request]:
        """
        Retrieves all Requests currently awaiting review.
        
        Returns:
            List[Request]: A collection of requests with RequestStatus.PENDING.
        """
        pass

    @abstractmethod
    def save(self, request: Request) -> None:
        """
        Persists a new request or updates an existing one in the data store.
        
        Args:
            request (Request): The request entity instance to be saved.
        """
        pass