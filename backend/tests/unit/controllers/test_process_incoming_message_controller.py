import pytest
from flask import Flask
from unittest.mock import MagicMock, patch

# Fazemos o patch do decorador ANTES de importar o controller para ele não bloquear os testes
patch('app.infrastructure.middleware.security.signature_required', lambda f: f).start()

from app.controllers.process_incoming_message_controller import ProcessIncomingMessageController, incoming_message_routes
from app.application.dtos.commands import IncomingMessageCommand

if hasattr(ProcessIncomingMessageController.handle_webhook, '__wrapped__'):
    ProcessIncomingMessageController.handle_webhook = ProcessIncomingMessageController.handle_webhook.__wrapped__

@pytest.fixture
def mock_use_case():
    return MagicMock()

@pytest.fixture
def app(mock_use_case):
    app = Flask(__name__)
    app.config["VERIFY_TOKEN"] = "secret_token"
    
    blueprint = incoming_message_routes(mock_use_case)
    app.register_blueprint(blueprint)
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_verify_webhook_success(client):
    response = client.get('/webhook?hub.mode=subscribe&hub.verify_token=secret_token&hub.challenge=123456789')
    
    assert response.status_code == 200
    assert response.data.decode('utf-8') == '123456789'

def test_verify_webhook_fails_with_wrong_token(client):
    response = client.get('/webhook?hub.mode=subscribe&hub.verify_token=token_error&hub.challenge=123456789')
    
    assert response.status_code == 403
    assert response.get_json() == {"status": "error", "message": "Verification failed"}

def test_verify_webhook_fails_with_wrong_mode(client):
    response = client.get('/webhook?hub.mode=unsubscribe&hub.verify_token=secret_token&hub.challenge=123456789')
    
    assert response.status_code == 403

@patch('app.controllers.process_incoming_message_controller.map_whatsapp_json_to_result')
def test_handle_webhook_success(mock_mapper, client, mock_use_case):
    dto = IncomingMessageCommand(wa_id="123", sender_name="João", message_body="Hello")
    mock_mapper.return_value = dto

    response = client.post('/webhook', json={"entry": [{"changes": [{"value": {}}]}]})

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
    mock_mapper.assert_called_once()
    mock_use_case.execute.assert_called_once_with(dto)

@patch('app.controllers.process_incoming_message_controller.map_whatsapp_json_to_result')
def test_handle_webhook_ignored_message(mock_mapper, client, mock_use_case):
    mock_mapper.return_value = None
    
    response = client.post('/webhook', json={"random": "data"})
    
    assert response.status_code == 200
    assert response.get_json() == {"status": "ignored"}
    mock_use_case.execute.assert_not_called()

@patch('app.controllers.process_incoming_message_controller.map_whatsapp_json_to_result')
def test_handle_webhook_resilience_on_exception(mock_mapper, client, mock_use_case):
    dto = IncomingMessageCommand(wa_id="123", sender_name="João", message_body="Hello")
    mock_mapper.return_value = dto
    mock_use_case.execute.side_effect = Exception("Erro na Base de Dados")
    
    response = client.post('/webhook', json={"entry": []})
    
    assert response.status_code == 200
    assert response.get_json() == {"status": "error", "message": "Erro na Base de Dados"}
    
    mock_use_case.execute.assert_called_once()