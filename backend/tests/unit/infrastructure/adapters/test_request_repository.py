import pytest
import uuid
from unittest.mock import patch
from flask import Flask

from app.infrastructure.database import db
from app.infrastructure.adapters.persistence_adapters.orm_models import RequestORM
from app.infrastructure.adapters.persistence_adapters.request_repository import RequestRepository
from app.domain.entities.entities import Request, RequestStatus


@pytest.fixture
def app_context():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all() 
        yield app       
        db.session.remove()
        db.drop_all()  

@pytest.fixture
def repo(app_context):
    return RequestRepository()

@pytest.fixture
def base_request():
    return Request(
        wa_id="351900000000",
        customer_name="Rui",
        intent="update_nif",
        user_input="Quero mudar o meu nif",
        field_value="123456789",
        generated_response="Vou tratar disso.",
        simulation_data={"status": "ok"}
    )


def test_save_new_request(repo, base_request):
    repo.save(base_request)
    
    saved_orm = db.session.query(RequestORM).filter_by(uid=str(base_request.uid)).first()
    
    assert saved_orm is not None
    assert saved_orm.customer_name == "Rui"
    assert saved_orm.wa_id == "351900000000"
    assert saved_orm.status == "PENDING"
    assert saved_orm.simulation_data == {"status": "ok"}

def test_save_existing_request(repo, base_request):
    repo.save(base_request)

    base_request.approve()
    base_request.generated_response = "Aprovado pelo Admin"
    
    repo.save(base_request)
    
    count = db.session.query(RequestORM).count()
    assert count == 1
    
    updated_orm = db.session.query(RequestORM).first()
    assert updated_orm.status == "APPROVED"
    assert updated_orm.generated_response == "Aprovado pelo Admin"
    assert updated_orm.processed_at is not None

def test_get_by_id_success(repo, base_request):
    repo.save(base_request)

    found_request = repo.get_by_id(base_request.uid)

    assert found_request is not None
    assert isinstance(found_request, Request)
    assert found_request.uid == base_request.uid
    assert found_request.customer_name == "Rui"

def test_get_by_id_not_found(repo):
    found_request = repo.get_by_id(uuid.uuid4())
    assert found_request is None

def test_get_all_pending(repo, base_request):
    repo.save(base_request)

    approved_req = Request(wa_id="123", customer_name="Ana", intent="x", user_input="y", field_value="z", generated_response="ok")
    approved_req.approve()
    repo.save(approved_req)
    
    pending_requests = repo.get_all_pending()

    assert len(pending_requests) == 1
    assert pending_requests[0].uid == base_request.uid
    assert pending_requests[0].status == RequestStatus.PENDING

@patch("app.infrastructure.adapters.persistence_adapters.request_repository.db.session.commit")
def test_save_rollback_on_error(mock_commit, repo, base_request):
    mock_commit.side_effect = Exception("Disco Cheio")
    
    with pytest.raises(RuntimeError, match="Database error while saving Request: Disco Cheio"):
        repo.save(base_request)