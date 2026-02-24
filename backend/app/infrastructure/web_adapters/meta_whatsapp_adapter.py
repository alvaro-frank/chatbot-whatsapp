# ==============================================================================
# FILE: app/infrastructure/meta_whatsapp_adapter.py
# DESCRIPTION: Infrastructure Adapter for Meta's WhatsApp Business Graph API.
#              Implements the WhatsAppProvider interface to decouple the 
#              messaging transport logic from the domain core.
# ==============================================================================

import requests
import logging
from app.domain.interfaces import WhatsAppProvider

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
        self.url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"
        self.headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def send_text_message(self, recipient_id: str, message_text: str) -> bool:
        """
        Dispatches a standardized text message through Meta's infrastructure.
        
        This method translates domain intents into the specific JSON schema 
        required by the 'whatsapp' messaging product.
        
        Args:
            recipient_id (str): The target phone number in international format.
            message_text (str): The content of the message to be delivered.
            
        Returns:
            bool: True if the API returns a 2xx status code, False otherwise.
            
        Note:
            We use a 10-second timeout to prevent blocking the service 
            in case of network congestion or API latency.
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_id,
            "type": "text",
            "text": {"preview_url": False, "body": message_text},
        }

        try:
            response = requests.post(self.url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Meta API Error: {e}")
            return False