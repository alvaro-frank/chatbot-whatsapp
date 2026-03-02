import pytest
import json
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from app import create_app
from app.infrastructure.database import db
from app.infrastructure.adapters.persistence_adapters.orm_models import RequestORM
from app.domain.entities.entities import MessageAnalysis

# --- Configuração do Ambiente de Integração ---

@pytest.fixture
def app():
    """Cria a aplicação com configuração de teste injetada para isolamento total."""
    # 1. Definimos a configuração de teste (BD em memória e chaves falsas)
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "VERIFY_TOKEN": "token_teste",
        "GROQ_API_KEY": "fake_key",
        "ACCESS_TOKEN": "fake_token",
        "PHONE_NUMBER_ID": "fake_id"
    }
    
    # 2. Criamos a app passando a config (Point 1 que aplicaste)
    app = create_app(test_config)

    with app.app_context():
        db.create_all() # Cria as tabelas na BD em memória
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente para chamadas HTTP."""
    return app.test_client()

# --- Testes de Integração Corrigidos ---

@patch("app.infrastructure.adapters.web_adapters.groq_adapter.GroqAdapter.analyze_message")
def test_full_webhook_to_dashboard_flow(mock_analyze, client):
    """Fluxo: Mensagem do WhatsApp -> Análise IA -> Gravação BD -> Dashboard Admin."""
    # Configuramos o mock para devolver uma intenção que CRIA um pedido (acionável)
    mock_analyze.return_value = MessageAnalysis(
        detected_language="pt",
        intent="alterar_nif",
        field_value="987654321",
        confidence_score=0.99,
        response_draft="Olá João, vou registar o seu NIF 987654321."
    )

    whatsapp_payload = {
        "entry": [{"changes": [{"value": {
            "contacts": [{"profile": {"name": "João"}, "wa_id": "351912345678"}],
            "messages": [{"type": "text", "text": {"body": "Mudar nif"}}]
        }}]}]
    }
    
    # POST Webhook (Simulamos a entrada da mensagem)
    with patch('app.infrastructure.middleware.security.signature_required', lambda f: f):
        client.post('/webhook', json=whatsapp_payload)
    
    # GET Dashboard (Verificamos se o pedido aparece na lista)
    response_admin = client.get('/admin/requests/')
    data = response_admin.get_json()
    
    assert len(data) == 1
    assert data[0]["customer"] == "João"
    assert data[0]["response_text"] == "Olá João, vou registar o seu NIF 987654321."


@patch("app.infrastructure.adapters.web_adapters.groq_adapter.GroqAdapter.analyze_message")
@patch("app.infrastructure.adapters.web_adapters.meta_whatsapp_adapter.httpx.post")
def test_non_actionable_message_flow(mock_ws, mock_analyze, client):
    """Garante que mensagens comuns (ex: 'Olá') NÃO sujam o dashboard admin."""
    # Configuramos o mock para uma intenção NÃO acionável
    mock_analyze.return_value = MessageAnalysis(
        detected_language="pt",
        intent="outro", 
        field_value=None,
        confidence_score=1.0,
        response_draft="Olá! Em que posso ajudar?"
    )
    mock_ws.return_value = MagicMock(status_code=200)

    payload = {
        "entry": [{"changes": [{"value": {
            "contacts": [{"profile": {"name": "Ana"}, "wa_id": "123"}],
            "messages": [{"type": "text", "text": {"body": "Olá"}}]
        }}]}]
    }

    with patch('app.infrastructure.middleware.security.signature_required', lambda f: f):
        client.post('/webhook', json=payload)

    # O Dashboard deve estar vazio (assert 0 == 0)
    response_admin = client.get('/admin/requests/')
    assert len(response_admin.get_json()) == 0


def test_admin_approval_integration(client, app):
    """Fluxo: Aprovação no Dashboard -> Atualização BD -> Notificação WhatsApp."""
    # 1. Inserimos um pedido manualmente (precisa de created_at para não dar IntegrityError)
    with app.app_context():
        req = RequestORM(
            uid="550e8400-e29b-41d4-a716-446655440000",
            wa_id="351912345678",
            customer_name="Maria",
            intent="alterar_morada",
            status="PENDING",
            generated_response="Texto base",
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(req)
        db.session.commit()

    # 2. Simulamos a aprovação pelo administrador
    with patch("app.infrastructure.adapters.web_adapters.meta_whatsapp_adapter.httpx.post") as mock_ws:
        mock_ws.return_value = MagicMock(status_code=200)
        
        response = client.post(
            '/admin/requests/550e8400-e29b-41d4-a716-446655440000/approve', 
            json={"response_text": "OK Maria!"}
        )

        assert response.status_code == 200
        mock_ws.assert_called_once()


def test_webhook_verification_handshake(client):
    """Valida o handshake de segurança obrigatório da Meta."""
    challenge = "challenge_123"
    url = f'/webhook?hub.mode=subscribe&hub.verify_token=token_teste&hub.challenge={challenge}'
    
    response = client.get(url)
    
    assert response.status_code == 200
    assert response.data.decode('utf-8') == challenge