import pytest
from app.utils.whatsapp_parser import parse_whatsapp_message
from app.dtos.whatsapp_dto import IncomingMessageDTO

def test_parse_whatsapp_message_success():
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
    
    result = parse_whatsapp_message(payload)
    
    assert isinstance(result, IncomingMessageDTO)
    assert result.wa_id == "351912345678"
    assert result.sender_name == "João"
    assert result.message_body == "Quero alterar o meu NIF"

def test_parse_whatsapp_message_invalid_format():
    with pytest.raises(ValueError, match="Invalid WhatsApp message format"):
        parse_whatsapp_message({"invalid": "data"})