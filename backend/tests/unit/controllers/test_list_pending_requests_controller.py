import pytest
from flask import Flask
from unittest.mock import MagicMock

from app.controllers.list_pending_requests_controller import register_pending_requests_routes

@pytest.fixture
def mock_use_case():
    return MagicMock()

@pytest.fixture
def app(mock_use_case):
    """Cria uma app Flask de teste e regista o Blueprint de admin."""
    app = Flask(__name__)
    
    blueprint = register_pending_requests_routes(mock_use_case)
    app.register_blueprint(blueprint)
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_list_requests_success(client, mock_use_case):
    mock_dto_1 = MagicMock()
    mock_dto_1.model_dump.return_value = {"id": "123", "customer": "Alice", "intent": "update_nif"}
    
    mock_dto_2 = MagicMock()
    mock_dto_2.model_dump.return_value = {"id": "456", "customer": "Bob", "intent": "update_email"}
    
    mock_use_case.execute.return_value = [mock_dto_1, mock_dto_2]
    
    response = client.get('/admin/requests/')
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["customer"] == "Alice"
    assert data[1]["customer"] == "Bob"
    
    mock_use_case.execute.assert_called_once()


def test_list_requests_handles_exception(client, mock_use_case):
    mock_use_case.execute.side_effect = Exception("Database Connection Lost")
    
    response = client.get('/admin/requests/')
    
    assert response.status_code == 500
    
    data = response.get_json()
    assert data == {"error": "Dashboard loading error"}
    
    mock_use_case.execute.assert_called_once()