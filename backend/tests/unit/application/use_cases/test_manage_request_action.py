import pytest
import uuid
from unittest.mock import MagicMock

from app.application.use_cases.manage_request_action import ManageRequestActionUseCase
from app.domain.entities.entities import Request, RequestStatus
from app.application.dtos.commands import ManageRequestCommand

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def mock_whatsapp_port():
    return MagicMock()

@pytest.fixture
def use_case(mock_repo, mock_whatsapp_port):
    return ManageRequestActionUseCase(repo=mock_repo, whatsapp_Port=mock_whatsapp_port)

@pytest.fixture
def pending_request():
    return Request(
        wa_id="351912345678",
        customer_name="Carlos",
        intent="update_nif",
        user_input="Change tax number",
        field_value="123456789",
        generated_response="AI Generated Text"
    )


def test_approve_success_with_default_text(use_case, mock_repo, mock_whatsapp_port, pending_request):
    req_id = str(pending_request.uid)
    mock_repo.get_by_id.return_value = pending_request
    command = ManageRequestCommand(request_id=req_id, action="APPROVE", override_text=None)

    result = use_case.approve(command)

    assert result.new_status == RequestStatus.APPROVED.value
    assert result.request_id == req_id
    
    mock_repo.get_by_id.assert_called_once_with(uuid.UUID(req_id))
    mock_repo.save.assert_called_once_with(pending_request)
    
    mock_whatsapp_port.send_text_message.assert_called_once_with("351912345678", "AI Generated Text")
    
    assert pending_request.status == RequestStatus.APPROVED
    assert pending_request.generated_response == "AI Generated Text"

def test_approve_success_with_override_text(use_case, mock_repo, mock_whatsapp_port, pending_request):
    req_id = str(pending_request.uid)
    mock_repo.get_by_id.return_value = pending_request
    command = ManageRequestCommand(request_id=req_id, action="APPROVE", override_text="Admin Text")

    use_case.approve(command)

    mock_whatsapp_port.send_text_message.assert_called_once_with("351912345678", "Admin Text")

    assert pending_request.generated_response == "Admin Text"

def test_approve_fails_if_request_not_found(use_case, mock_repo):
    mock_repo.get_by_id.return_value = None
    command = ManageRequestCommand(request_id=str(uuid.uuid4()), action="APPROVE")

    with pytest.raises(ValueError, match="Request not found."):
        use_case.approve(command)

def test_approve_resilience_if_whatsapp_fails(use_case, mock_repo, mock_whatsapp_port, pending_request):
    mock_repo.get_by_id.return_value = pending_request
    mock_whatsapp_port.send_text_message.side_effect = Exception("WhatsApp API Down")
    command = ManageRequestCommand(request_id=str(pending_request.uid), action="APPROVE")

    result = use_case.approve(command)

    assert result.new_status == RequestStatus.APPROVED.value
    mock_repo.save.assert_called_once()
    assert pending_request.status == RequestStatus.APPROVED

def test_reject_success_with_default_text(use_case, mock_repo, mock_whatsapp_port, pending_request):
    req_id = str(pending_request.uid)
    mock_repo.get_by_id.return_value = pending_request
    command = ManageRequestCommand(request_id=req_id, action="REJECT", override_text=None)

    result = use_case.reject(command)

    assert result.new_status == RequestStatus.REJECTED.value
    mock_repo.save.assert_called_once_with(pending_request)
    mock_whatsapp_port.send_text_message.assert_called_once_with("351912345678", "AI Generated Text")
    assert pending_request.status == RequestStatus.REJECTED

def test_reject_success_with_override_text(use_case, mock_repo, mock_whatsapp_port, pending_request):
    req_id = str(pending_request.uid)
    mock_repo.get_by_id.return_value = pending_request
    command = ManageRequestCommand(request_id=req_id, action="REJECT", override_text="Rejected by shortage os data")

    use_case.reject(command)

    mock_whatsapp_port.send_text_message.assert_called_once_with("351912345678", "Rejected by shortage os data")
    assert pending_request.generated_response == "Rejected by shortage os data"

def test_reject_resilience_if_whatsapp_fails(use_case, mock_repo, mock_whatsapp_port, pending_request):
    mock_repo.get_by_id.return_value = pending_request
    mock_whatsapp_port.send_text_message.side_effect = Exception("WhatsApp API Down")
    command = ManageRequestCommand(request_id=str(pending_request.uid), action="REJECT")

    result = use_case.reject(command)

    assert result.new_status == RequestStatus.REJECTED.value
    mock_repo.save.assert_called_once()
    assert pending_request.status == RequestStatus.REJECTED