import pytest
from datetime import timezone
from app.domain.entities.entities import Request, RequestStatus, ReceivedMessage

"""
Requests Entity Tests
"""
@pytest.fixture
def base_request():
    return Request(
        wa_id="351912345678",
        customer_name="João Silva",
        intent="update_email",
        user_input="I want to change my tax number to 123456789",
        field_value="123456789",
        generated_response="O seu pedido foi registado."
    )

def test_request_approve_success(base_request):
    base_request.approve()
    
    assert base_request.status == RequestStatus.APPROVED
    assert base_request.processed_at is not None
    assert base_request.processed_at.tzinfo == timezone.utc

def test_request_approve_fails_if_already_approved(base_request):
    # Arrange
    base_request.approve() # Fica APPROVED
    
    # Act & Assert
    with pytest.raises(ValueError, match="Approve Request Error: Request is already APPROVED."):
        base_request.approve()

def test_request_reject_success(base_request):
    # Act
    base_request.reject()
    
    # Assert
    assert base_request.status == RequestStatus.REJECTED
    assert base_request.processed_at is not None
    assert base_request.processed_at.tzinfo == timezone.utc

def test_request_reject_fails_if_already_rejected(base_request):
    # Arrange
    base_request.reject() # Fica REJECTED
    
    # Act & Assert
    with pytest.raises(ValueError, match="Reject Request Error: Request is already REJECTED."):
        base_request.reject()

# --- Testes para a Entidade ReceivedMessage ---

def test_received_message_first_name_with_full_name():
    msg = ReceivedMessage(sender_id="123", sender_name="Ana Maria Braga", content="Hello")
    assert msg.first_name == "Ana"

def test_received_message_first_name_with_single_name():
    msg = ReceivedMessage(sender_id="123", sender_name="Carlos", content="Hello")
    assert msg.first_name == "Carlos"

def test_received_message_first_name_with_empty_name():
    msg = ReceivedMessage(sender_id="123", sender_name="", content="Hello")
    assert msg.first_name == ""