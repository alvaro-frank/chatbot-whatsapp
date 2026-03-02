import pytest
from app.infrastructure.mappers.whatsapp_json_result_mapper import map_whatsapp_json_to_result
from app.application.dtos.commands import IncomingMessageCommand

def test_map_whatsapp_json_to_result_success():
    valid_payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "contacts": [{"profile": {"name": "João Silva"}, "wa_id": "351912345678"}],
                    "messages": [{"type": "text", "text": {"body": "I want to change my tax number"}}]
                }
            }]
        }]
    }
    
    result = map_whatsapp_json_to_result(valid_payload)
    
    assert isinstance(result, IncomingMessageCommand)
    assert result.wa_id == "351912345678"
    assert result.sender_name == "João Silva"
    assert result.message_body == "I want to change my tax number"

def test_map_whatsapp_json_to_result_ignores_status_updates():
    status_payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "statuses": [{"id": "wamid.123", "status": "read"}]
                }
            }]
        }]
    }
    
    result = map_whatsapp_json_to_result(status_payload)
    assert result is None

def test_map_whatsapp_json_to_result_ignores_non_text_messages():
    image_payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "contacts": [{"profile": {"name": "João Silva"}, "wa_id": "351912345678"}],
                    "messages": [{"type": "image", "image": {"id": "img_123"}}]
                }
            }]
        }]
    }
    
    result = map_whatsapp_json_to_result(image_payload)
    assert result is None

def test_map_whatsapp_json_to_result_handles_key_errors():
    malformed_payload = {"random_data": "not_what_we_expect"}
    
    result = map_whatsapp_json_to_result(malformed_payload)
    assert result is None

def test_map_whatsapp_json_to_result_handles_index_errors():
    empty_arrays_payload = {
        "entry": []
    }
    
    result = map_whatsapp_json_to_result(empty_arrays_payload)
    assert result is None