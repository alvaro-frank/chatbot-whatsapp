# ==============================================================================
# FILE: app/infrastructure/mappers.py
# DESCRIPTION: Data mappers for infrastructure-to-domain transformation.
#              Responsible for translating external payloads (Meta JSON) into 
#              internal Data Transfer Objects (DTOs).
# ==============================================================================

import logging
from app.dtos.dtos import IncomingMessageDTO

def map_whatsapp_json_to_dto(body: dict) -> IncomingMessageDTO:
    """
    Translates Meta's complex JSON structure into a clean IncomingMessageDTO.
    
    Returns:
        IncomingMessageDTO: If the payload contains a valid text message.
        None: If the payload is a status update (delivered/read) or unsupported type.
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