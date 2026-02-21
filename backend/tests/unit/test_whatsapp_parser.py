import pytest
from app.infrastructure.mappers import map_whatsapp_json_to_dto
from app.dtos.dtos import IncomingMessageDTO

def test_map_whatsapp_json_to_dto_success():
    # Dados de exemplo simulando o webhook da Meta
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "contacts": [{"wa_id": "351912345678", "profile": {"name": "João"}}],
                    "messages": [{"text": {"body": "Quero alterar o meu NIF"}}]
                }
            }]
        }]
    }
    
    result = map_whatsapp_json_to_dto(payload)
    
    assert isinstance(result, IncomingMessageDTO)
    assert result.wa_id == "351912345678"
    assert result.sender_name == "João"
    assert result.message_body == "Quero alterar o meu NIF"

def test_map_whatsapp_json_to_dto_invalid_format():
    with pytest.raises(ValueError, match="Invalid WhatsApp message format"):
        map_whatsapp_json_to_dto({"invalid": "data"})