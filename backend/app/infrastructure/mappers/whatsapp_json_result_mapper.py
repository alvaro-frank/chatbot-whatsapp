import logging
from app.application.dtos.commands import IncomingMessageCommand
from typing import Dict

def map_whatsapp_json_to_result(body: Dict) -> IncomingMessageCommand:
    """
    Translates Meta's complex JSON structure into a clean IncomingMessageCommand.

    This function acts as a Data Mapper, specifically handling the Webhook 
    notification format from the Meta Graph API. It extracts identity and 
    content while ignoring non-message metadata (like status updates).

    Args:
        body (Dict): The raw JSON payload received from the WhatsApp Webhook.

    Returns:
        IncomingMessageCommand: A validated object containing sender info and text.

    Raises:
        ValueError: If the required keys (wa_id, name, or body) are missing or 
                    if the structure does not match the expected message format.
    """
    try:
        value = body["entry"][0]["changes"][0]["value"]
        
        if "messages" not in value or "contacts" not in value:
            return None
            
        contact = value["contacts"][0]
        message = value["messages"][0]
        
        if message.get("type") != "text":
            logging.info(f"Unsupported message type: {message.get('type')}")
            return None

        return IncomingMessageCommand(
            wa_id=contact["wa_id"],
            sender_name=contact["profile"]["name"],
            message_body=message["text"]["body"]
        )
    except (KeyError, IndexError):
        return None