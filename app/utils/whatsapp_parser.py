# ==============================================================================
# FILE: app/utils/whatsapp_parser.py
# DESCRIPTION: Logic to parse raw WhatsApp webhook JSON into a DTO.
# ==============================================================================

from app.dtos.dtos import IncomingMessageDTO

def parse_whatsapp_message(body: dict) -> IncomingMessageDTO:
    """
    Parses the complex Meta JSON structure into a clean DTO.
    """
    try:
        entry = body["entry"][0]["changes"][0]["value"]
        contact = entry["contacts"][0]
        message = entry["messages"][0]

        return IncomingMessageDTO(
            wa_id=contact["wa_id"],
            sender_name=contact["profile"]["name"],
            message_body=message["text"]["body"]
        )
    except (KeyError, IndexError) as e:
        raise ValueError(f"Invalid WhatsApp message format: {e}")