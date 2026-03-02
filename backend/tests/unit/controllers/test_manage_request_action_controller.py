import pytest
from flask import Flask
from unittest.mock import MagicMock, ANY

from app.controllers.manage_request_action_controller import register_manage_requests_routes
from app.application.ports.ports import NotificationDeliveryError

@pytest.fixture
def mock_use_case():
    return MagicMock()

@pytest.fixture
def app(mock_use_case):
    """Cria a app Flask de teste e regista o Blueprint de gestão de pedidos."""
    app = Flask(__name__)
    blueprint = register_manage_requests_routes(mock_use_case)
    app.register_blueprint(blueprint)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_result():
    """Simula o DTO de resultado que o Use Case devolve."""
    result = MagicMock()
    result.model_dump.return_value = {
        "request_id": "123",
        "customer": "Carlos",
        "new_status": "APPROVED",
        "message": "Sucesso"
    }
    return result

def test_approve_request_success_with_override(client, mock_use_case, mock_result):
    mock_use_case.approve.return_value = mock_result
    
    response = client.post('/123/approve', json={"response_text": "Texto do Admin"})
    
    assert response.status_code == 200
    assert response.get_json()["new_status"] == "APPROVED"
    
    called_command = mock_use_case.approve.call_args[0][0]
    assert called_command.request_id == "123"
    assert called_command.override_text == "Texto do Admin"

def test_approve_request_success_without_override(client, mock_use_case, mock_result):
    mock_use_case.approve.return_value = mock_result
    
    response = client.post('/123/approve', json={}) 
    
    assert response.status_code == 200
    called_command = mock_use_case.approve.call_args[0][0]
    assert called_command.override_text is None

def test_approve_request_value_error(client, mock_use_case):
    mock_use_case.approve.side_effect = ValueError("Request not found.")
    
    response = client.post('/123/approve', json={})
    
    assert response.status_code == 400
    assert response.get_json() == {"status": "error", "message": "Request not found."}

def test_approve_request_notification_error(client, mock_use_case):
    mock_use_case.approve.side_effect = NotificationDeliveryError("Timeout Meta API")
    
    response = client.post('/123/approve', json={})
    
    assert response.status_code == 502
    assert "Whatsapp Notification Error" in response.get_json()["message"]

def test_approve_request_internal_error(client, mock_use_case):
    mock_use_case.approve.side_effect = Exception("DB Crash")
    
    response = client.post('/123/approve', json={})
    
    assert response.status_code == 500


def test_reject_request_success(client, mock_use_case, mock_result):
    mock_result.model_dump.return_value["new_status"] = "REJECTED"
    mock_use_case.reject.return_value = mock_result
    
    response = client.post('/123/reject', json={"response_text": "Faltam documentos."})
    
    assert response.status_code == 200
    assert response.get_json()["new_status"] == "REJECTED"
    
    called_command = mock_use_case.reject.call_args[0][0]
    assert called_command.request_id == "123"
    assert called_command.override_text == "Faltam documentos."

def test_reject_request_value_error(client, mock_use_case):
    mock_use_case.reject.side_effect = ValueError("Already rejected.")
    
    response = client.post('/123/reject', json={})
    
    assert response.status_code == 400

def test_reject_request_notification_error(client, mock_use_case):
    mock_use_case.reject.side_effect = NotificationDeliveryError("API Down")
    
    response = client.post('/123/reject', json={})
    
    assert response.status_code == 502

def test_reject_request_internal_error(client, mock_use_case):
    mock_use_case.reject.side_effect = Exception("Out of Memory")
    
    response = client.post('/123/reject', json={})
    
    assert response.status_code == 500