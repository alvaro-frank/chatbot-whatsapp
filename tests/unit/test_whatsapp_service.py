from unittest.mock import MagicMock
from app.services.whatsapp_service import WhatsAppService
from app.dtos.whatsapp_dto import IncomingMessageDTO

def test_process_incoming_message_ignores_outro_intent():
    mock_repo = MagicMock()
    mock_ai = MagicMock()
    
    mock_ai.analyze_message.return_value = {"intent": "outro"}
    
    service = WhatsAppService(repo=mock_repo, ai_service=mock_ai)
    dto = IncomingMessageDTO(wa_id="1", sender_name="Ana", message_body="Olá")
    
    service.process_incoming_message(dto)
    
    mock_repo.add.assert_not_called()

def test_process_incoming_message_saves_valid_intent():
    mock_repo = MagicMock()
    mock_ai = MagicMock()
    
    mock_ai.analyze_message.return_value = {
        "intent": "alterar_nif",
        "field_value": "123456789",
        "response_draft": "Obrigado João, vamos processar."
    }
    
    service = WhatsAppService(repo=mock_repo, ai_service=mock_ai)
    dto = IncomingMessageDTO(wa_id="1", sender_name="João", message_body="NIF 123")
    
    service.process_incoming_message(dto)
    
    assert mock_repo.add.called