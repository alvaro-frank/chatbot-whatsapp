# ==============================================================================
# FILE: app/domain/interfaces.py
# DESCRIPTION: Abstract Base Classes (Interfaces) for the Domain Layer.
#              This file implements the Dependency Inversion Principle, 
#              ensuring that business logic does not depend on infrastructure 
#              details (adapters).
# ==============================================================================

from abc import ABC, abstractmethod
from app.dtos.whatsapp_dto import AIAnalysisDTO

class LLMProvider(ABC):
    """
    Contract for Large Language Model (LLM) implementations.
    
    This interface abstracts the intelligence layer. Implementations are 
    responsible for translating unstructured natural language into structured 
    domain insights (Intents, Entities, and Sentiment).
    """

    @abstractmethod
    def analyze_message(self, message_body: str, user_name: str) -> AIAnalysisDTO:
        """
        Interprets a user message and extracts business-critical information.
        
        Args:
            message_body (str): The raw text received from the messaging platform.
            user_name (str): The sender's name to provide personalized context 
                             for the AI model.
            
        Returns:
            AIAnalysisDTO: A structured object containing the classified intent, 
                           extracted fields, and a suggested response draft.
                           
        Raises:
            Exception: If the AI provider is unreachable or the response fails 
                       to meet the DTO schema requirements.
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
    def send_text_message(self, recipient_id: str, message_text: str) -> bool:
        """
        Dispatches a text message to an external recipient.
        
        Args:
            recipient_id (str): The unique identifier of the recipient (WA_ID).
            message_text (str): The final validated text to be sent.
            
        Returns:
            bool: True if the external API acknowledged the request with a 
                  success status code; False otherwise.
                  
        Note:
            Implementations should handle low-level concerns like JSON 
            serialization and HTTP headers.
        """
        pass