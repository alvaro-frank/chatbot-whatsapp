import logging
from app.dtos.dtos import IncomingMessageDTO

def map_whatsapp_json_to_dto(body: dict) -> IncomingMessageDTO:
    """
    Translates Meta's complex JSON structure into a clean IncomingMessageDTO.

    This function acts as a Data Mapper, specifically handling the Webhook 
    notification format from the Meta Graph API. It extracts identity and 
    content while ignoring non-message metadata (like status updates).

    Args:
        body (dict): The raw JSON payload received from the WhatsApp Webhook.

    Returns:
        IncomingMessageDTO: A validated object containing sender info and text.

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

        return IncomingMessageDTO(
            wa_id=contact["wa_id"],
            sender_name=contact["profile"]["name"],
            message_body=message["text"]["body"]
        )
    except (KeyError, IndexError):
        return None