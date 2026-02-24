import uuid
from typing import Optional, List
from app.domain.interfaces import IRequestRepository
from app.domain.entities import Request, RequestStatus
from app.infrastructure.database import db
from app.infrastructure.persistence_adapters.orm_models import RequestORM

class RequestRepository(IRequestRepository):
    """
    SQLAlchemy implementation of the Request Repository.
    
    Handles the persistence logic for Request entities, including the mapping 
    between Domain Entities and ORM Models (Data Mappers).
    """

    def _to_domain(self, orm_model: Optional[RequestORM]) -> Optional[Request]:
        """
        Maps a database-specific ORM model to a pure Domain Entity.
        
        Args:
            orm_model (Optional[RequestORM]): The database record.
            
        Returns:
            Optional[Request]: The domain-valid Request object or None.
        """
        if not orm_model:
            return None
            
        return Request(
            uid=uuid.UUID(orm_model.uid),
            wa_id=orm_model.wa_id,
            customer_name=orm_model.customer_name,
            intent=orm_model.intent,
            user_input=orm_model.user_input,
            field_value=orm_model.field_value,
            generated_response=orm_model.generated_response,
            status=RequestStatus(orm_model.status), # Converte string de volta para Enum
            created_at=orm_model.created_at,
            processed_at=orm_model.processed_at
        )

    def _to_orm(self, domain_entity: Request, orm_model: Optional[RequestORM] = None) -> RequestORM:
        """
        Maps a Domain Entity to a database-specific ORM model.
        
        Args:
            domain_entity (Request): The domain object to be persisted.
            orm_model (Optional[RequestORM]): An existing ORM instance for updates.
            
        Returns:
            RequestORM: The prepared ORM model ready for SQLAlchemy session.
        """
        if not orm_model:
            orm_model = RequestORM(uid=str(domain_entity.uid))
            
        orm_model.wa_id = domain_entity.wa_id
        orm_model.customer_name = domain_entity.customer_name
        orm_model.intent = domain_entity.intent
        orm_model.user_input = domain_entity.user_input
        orm_model.field_value = domain_entity.field_value
        orm_model.generated_response = domain_entity.generated_response
        orm_model.status = domain_entity.status.value # Extrai a string do Enum
        orm_model.created_at = domain_entity.created_at
        orm_model.processed_at = domain_entity.processed_at
        
        return orm_model

    def get_by_id(self, uid: uuid.UUID) -> Optional[Request]:
        """
        Retrieves a Request by its UUID and converts it to a Domain Entity.
        
        Args:
            uid (uuid.UUID): The unique identifier of the request.
            
        Returns:
            Optional[Request]: The domain entity if found, otherwise None.
        """
        orm_model = db.session.query(RequestORM).filter_by(uid=str(uid)).first()
        return self._to_domain(orm_model)

    def get_all_pending(self) -> List[Request]:
        """
        Queries the database for all records with a 'PENDING' status.
        
        Returns:
            List[Request]: A list of domain entities awaiting processing.
        """
        orm_models = db.session.query(RequestORM).filter_by(status=RequestStatus.PENDING.value).all()
        return [self._to_domain(m) for m in orm_models]

    def save(self, request: Request) -> None:
        """
        Perists a Request entity to the database (Upsert logic).
        
        If the record exists, it is updated; otherwise, a new record is created.
        
        Args:
            request (Request): The domain entity to save.
            
        Raises:
            RuntimeError: If a database error occurs during commit.
        """
        orm_model = db.session.query(RequestORM).filter_by(uid=str(request.uid)).first()
        
        is_new = orm_model is None
        orm_model = self._to_orm(domain_entity=request, orm_model=orm_model)
        
        if is_new:
            db.session.add(orm_model)
            
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Database error while saving Request: {str(e)}")