import pytest
from unittest.mock import MagicMock, patch
from app.services.ai_service import AIService
from app.utils.whatsapp_parser import parse_whatsapp_message

def test_analyze_message_success(app):
    payload = { "entry": [{ "changes": [{ "value": {
        "contacts": [{"wa_id": "123", "profile": {"name": "João"}}],
        "messages": [{"text": {"body": "Olá"}}]
    }}]}] }
    result = parse_whatsapp_message(payload)
    assert result.wa_id == "123"

def test_analyze_message_no_client(app):
    with app.app_context():
        service = AIService()
        service.client = None
        
        result = service.analyze_message("olá", "User")
        assert result is None