import pytest
from unittest.mock import MagicMock

from app.application.use_cases.list_pending_requests import ListPendingRequestsUseCase
from app.domain.entities.entities import Request
from app.application.dtos.results import PendingRequestResult

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def use_case(mock_repo):
    return ListPendingRequestsUseCase(repo=mock_repo)


def test_execute_returns_mapped_results(use_case, mock_repo):
    req1 = Request(
        wa_id="351911111111", customer_name="Alice", intent="update_nif", 
        user_input="I want to change my tax number", field_value="123456789", generated_response="OK",
        simulation_data={"status": "simulated"}
    )
    req2 = Request(
        wa_id="351922222222", customer_name="Bob", intent="update_email", 
        user_input="Change email", field_value="bob@test.com", generated_response="OK",
        simulation_data={"status": "simulated"}
    )
    mock_repo.get_all_pending.return_value = [req1, req2]

    results = use_case.execute()

    mock_repo.get_all_pending.assert_called_once()
    assert len(results) == 2
    
    assert all(isinstance(r, PendingRequestResult) for r in results)
    assert results[0].wa_id == "351911111111"
    assert results[0].customer == "Alice"
    assert results[1].wa_id == "351922222222"
    assert results[1].customer == "Bob"

def test_execute_with_empty_repository(use_case, mock_repo):
    mock_repo.get_all_pending.return_value = []

    results = use_case.execute()

    mock_repo.get_all_pending.assert_called_once()
    assert results == []

def test_execute_skips_request_on_error(use_case, mock_repo):
    valid_req = Request(
        wa_id="351911111111", customer_name="Alice", intent="update_nif", 
        user_input="Mudar nif", field_value="123", generated_response="OK"
    )
    
    invalid_req = Request(
        wa_id="351922222222", customer_name="Bob", intent="update_email", 
        user_input="Change email", field_value="bob", generated_response="OK"
    )
    invalid_req.created_at = None 

    mock_repo.get_all_pending.return_value = [valid_req, invalid_req]

    results = use_case.execute()

    assert len(results) == 1
    assert results[0].customer == "Alice"