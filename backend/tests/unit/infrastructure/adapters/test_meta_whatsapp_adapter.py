import pytest
from unittest.mock import patch, MagicMock
import httpx

from app.infrastructure.adapters.web_adapters.meta_whatsapp_adapter import MetaWhatsAppAdapter
from app.application.ports.ports import NotificationDeliveryError

@pytest.fixture
def adapter():
    """Instancia o adaptador com credenciais de teste."""
    return MetaWhatsAppAdapter(token="token_secreto_teste", phone_number_id="123456789", version="v24.0")


@patch("app.infrastructure.adapters.web_adapters.meta_whatsapp_adapter.httpx.post")
def test_send_text_message_success(mock_post, adapter):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    adapter.send_text_message(recipient_id="351910000000", message_text="Olá, mundo!")

    expected_url = "https://graph.facebook.com/v24.0/123456789/messages"
    expected_headers = {
        "Authorization": "Bearer token_secreto_teste",
        "Content-Type": "application/json"
    }
    expected_payload = {
        "messaging_product": "whatsapp",
        "to": "351910000000",
        "type": "text",
        "text": {"body": "Olá, mundo!"}
    }
    
    mock_post.assert_called_once_with(
        expected_url,
        headers=expected_headers,
        json=expected_payload,
        timeout=10.0
    )
    mock_response.raise_for_status.assert_called_once()

@patch("app.infrastructure.adapters.web_adapters.meta_whatsapp_adapter.httpx.post")
def test_send_text_message_http_error(mock_post, adapter):
    mock_response = MagicMock()

    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "400 Bad Request", request=MagicMock(), response=MagicMock()
    )
    mock_post.return_value = mock_response

    with pytest.raises(NotificationDeliveryError, match="Failed to send WhatsApp message"):
        adapter.send_text_message("351910000000", "Olá")

@patch("app.infrastructure.adapters.web_adapters.meta_whatsapp_adapter.httpx.post")
def test_send_text_message_timeout_error(mock_post, adapter):
    mock_post.side_effect = httpx.TimeoutException("Connection Timeout")

    with pytest.raises(NotificationDeliveryError, match="Failed to send WhatsApp message"):
        adapter.send_text_message("351910000000", "Olá")