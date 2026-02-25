import requests
import logging
from app.domain.ports import WhatsAppProvider, NotificationDeliveryError
import httpx

class MetaWhatsAppAdapter(WhatsAppProvider):
    """
    Adapter for Meta's Cloud API (Graph API).
    
    Responsible for the low-level HTTP communication required to dispatch 
    messages. It handles headers, authentication, and payload construction 
    specific to the Meta messaging product.
    """
    def __init__(self, token: str, phone_number_id: str, version: str = "v24.0"):
        """
        Initializes the adapter with Meta credentials and endpoint metadata.
        
        Args:
            token (str): Permanent or temporary Meta Access Token.
            phone_number_id (str): The unique ID of the sender's phone number.
            version (str): The Meta Graph API version (default is v24.0).
        """
        self.token = token
        self.base_url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"
        self.headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def send_text_message(self, recipient_id: str, message_text: str) -> None:
        """
        Dispatches a standardized text message through Meta's infrastructure.
        
        This method translates domain intents into the specific JSON schema 
        required by the 'whatsapp' messaging product.
        
        Args:
            recipient_id (str): The target phone number in international format.
            message_text (str): The content of the message to be delivered.
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "text",
            "text": {"body": message_text}
        }

        try:
            response = httpx.post(self.base_url, headers=headers, json=payload, timeout=10.0)
            response.raise_for_status()
            
            logging.info(f"WhatsApp message successfully sent to {recipient_id}")
            return None
            
        except Exception as e:
            logging.error(f"❌ Meta API Error: Fail sending message to {recipient_id}. Details: {str(e)}")
            raise NotificationDeliveryError(f"Failed to send WhatsApp message: {e}")