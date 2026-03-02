import pytest
from unittest.mock import MagicMock, patch
from app.application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from app.domain.entities.entities import MessageAnalysis
from app.application.dtos.commands import IncomingMessageCommand

@pytest.fixture
def mock_llm_port():
    return MagicMock()

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def use_case(mock_llm_port, mock_repo):
    return ProcessIncomingMessageUseCase(llm_Port=mock_llm_port, repo=mock_repo)

@patch('app.application.use_cases.process_incoming_message.CommandFactory')
def test_execute_with_actionable_intent_saves_request(mock_factory, use_case, mock_llm_port, mock_repo):
    dto = IncomingMessageCommand(wa_id="351912345678", sender_name="João Silva", message_body="I want to change my tax number to 123456789")
    
    mock_analysis = MessageAnalysis(
        detected_language="pt",
        intent="update_nif",
        field_value="123456789",
        confidence_score=0.95,
        response_draft="I'll register the request"
    )
    mock_llm_port.analyze_message.return_value = mock_analysis
    
    mock_factory.is_actionable_intent.return_value = True
    
    mock_command = MagicMock()
    mock_command.execute.return_value = {"status": "simulated", "new_nif": "123456789"}
    mock_factory.get_command.return_value = mock_command
    
    use_case.execute(dto)
    
    mock_llm_port.analyze_message.assert_called_once_with(
        message_body="I want to change my tax number to 123456789",
        user_name="João"
    )
    
    mock_command.execute.assert_called_once_with(mock_analysis)
    
    mock_repo.save.assert_called_once()
    
    saved_request = mock_repo.save.call_args[0][0]
    assert saved_request.wa_id == "351912345678"
    assert saved_request.intent == "update_nif"
    assert saved_request.simulation_data == {"status": "simulated", "new_nif": "123456789"}
    
@patch('app.application.use_cases.process_incoming_message.CommandFactory')
def test_execute_with_non_actionable_intent_ignores_request(mock_factory, use_case, mock_llm_port, mock_repo):
    dto = IncomingMessageCommand(wa_id="351912345678", sender_name="Maria", message_body="Olá, bom dia!")
    
    mock_analysis = MessageAnalysis(
        detected_language="pt",
        intent="greeting",
        field_value=None,
        confidence_score=0.99,
        response_draft="Olá, Maria! Como posso ajudar hoje?"
    )
    mock_llm_port.analyze_message.return_value = mock_analysis
    
    mock_factory.is_actionable_intent.return_value = False
    
    use_case.execute(dto)
    
    mock_llm_port.analyze_message.assert_called_once_with(
        message_body="Olá, bom dia!",
        user_name="Maria"
    )
    
    mock_factory.get_command.assert_not_called()
    mock_repo.save.assert_not_called()