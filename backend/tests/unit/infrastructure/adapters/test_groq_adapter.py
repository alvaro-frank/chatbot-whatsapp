import pytest
from unittest.mock import patch, MagicMock

from app.infrastructure.adapters.web_adapters.groq_adapter import GroqAdapter
from app.domain.entities.entities import MessageAnalysis

def test_groq_adapter_init_fails_without_api_key():
    with pytest.raises(ValueError, match="Groq API Key is required"):
        GroqAdapter(api_key=None)
    
    with pytest.raises(ValueError, match="Groq API Key is required"):
        GroqAdapter(api_key="")

def test_groq_adapter_init_success():
    adapter = GroqAdapter(api_key="gsk_super_secret_key")
    assert adapter.model == "llama-3.3-70b-versatile"


@pytest.fixture
def mock_groq_client():
    with patch('app.infrastructure.adapters.web_adapters.groq_adapter.Groq') as MockGroq:
        mock_instance = MockGroq.return_value
        yield mock_instance

@pytest.fixture
def adapter(mock_groq_client):
    return GroqAdapter(api_key="test_key")


def test_analyze_message_success(adapter, mock_groq_client):
    valid_json_string = """
    {
        "detected_language": "pt",
        "intent": "alterar_nif",
        "field_value": "123456789",
        "confidence_score": 0.95,
        "response_draft": "Claro, João. Vou registar o novo NIF."
    }
    """
    mock_message = MagicMock()
    mock_message.content = valid_json_string
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    
    mock_groq_client.chat.completions.create.return_value = mock_completion

    result = adapter.analyze_message(message_body="Quero mudar o meu NIF para 123456789", user_name="João")

    assert isinstance(result, MessageAnalysis)
    assert result.detected_language == "pt"
    assert result.intent == "alterar_nif"
    assert result.field_value == "123456789"
    assert result.confidence_score == 0.95
    assert result.response_draft == "Claro, João. Vou registar o novo NIF."
    
    mock_groq_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_groq_client.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "llama-3.3-70b-versatile"
    assert call_kwargs["response_format"] == {"type": "json_object"}
    assert call_kwargs["temperature"] == 0

def test_analyze_message_invalid_json_format(adapter, mock_groq_client):
    invalid_json_string = '{"intent": "alterar_nif"}' 
    
    mock_message = MagicMock()
    mock_message.content = invalid_json_string
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    
    mock_groq_client.chat.completions.create.return_value = mock_completion

    with pytest.raises(ConnectionError, match="Failed to get analysis from Groq"):
        adapter.analyze_message("Olá", "João")

def test_analyze_message_network_failure(adapter, mock_groq_client):
    mock_groq_client.chat.completions.create.side_effect = Exception("Groq API Timeout")

    with pytest.raises(ConnectionError, match="Failed to get analysis from Groq: Groq API Timeout"):
        adapter.analyze_message("Olá", "João")