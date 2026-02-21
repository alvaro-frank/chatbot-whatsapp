import pytest
from unittest.mock import MagicMock, patch
from app.services.ai_service import AIService
from app.infrastructure.mappers import map_whatsapp_json_to_dto

def test_analyze_message_success(app):
    payload = { "entry": [{ "changes": [{ "value": {
        "contacts": [{"wa_id": "123", "profile": {"name": "João"}}],
        "messages": [{"text": {"body": "Olá"}}]
    }}]}] }
    result = map_whatsapp_json_to_dto(payload)
    assert result.wa_id == "123"

def test_analyze_message_no_client(app):
    with app.app_context():
        service = AIService()
        service.client = None
        
        result = service.analyze_message("olá", "User")
        assert result is None