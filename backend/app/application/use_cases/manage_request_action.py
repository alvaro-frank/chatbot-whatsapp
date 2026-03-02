import logging
import uuid
from app.domain.ports.ports import WhatsAppPort, IRequestRepository
from app.application.dtos.commands import ManageRequestCommand
from app.application.dtos.results import ManageRequestResult
from app.domain.entities.entities import Request

class ManageRequestActionUseCase:
    """
    Use Case for executing administrative decisions on customer requests.
    
    This service orchestrates the transition of requests from PENDING to final 
    states (APPROVED/REJECTED) and manages the subsequent communication via WhatsApp.
    """
    def __init__(self, repo: IRequestRepository, whatsapp_Port: WhatsAppPort):
        """
        Initializes the use case with persistence and communication dependencies.
        
        Args:
            repo (IRequestRepository): Repository to fetch and update Request entities.
            whatsapp_Port (WhatsAppPort): Port to dispatch final notifications.
        """
        self.repo = repo
        self.whatsapp_Port = whatsapp_Port

    def approve(self, command: ManageRequestCommand) -> ManageRequestResult:
        """
        Finalizes a request as APPROVED and notifies the customer.
        
        This method updates the domain entity state, sets the final response text 
        (allowing for manual edits), dispatches the message, and persists the change.

        Args:
            

        Raises:
            ValueError: If the request ID is invalid or the record doesn't exist.
            NotificationDeliveryError: If the WhatsApp message fails to send.
            
        Returns:

        """
        req = self._get_request(command.request_id)
        final_text = command.override_text or req.generated_response

        req.approve()
        req.generated_response = final_text
        self.repo.save(req)
        
        try:
            self.whatsapp_Port.send_text_message(req.wa_id, final_text)
        except Exception as e:
            logging.error(f"Error sending WhatsApp message on request {req.uid} approval: {e}")
        
        return ManageRequestResult(
            request_id=str(req.uid),
            customer=req.customer_name,
            wa_id=req.wa_id,
            new_status=req.status.value,
            message=f"Pedido aprovado e {req.wa_id} ({req.customer_name}) notificado.",
            processed_at=req.processed_at.strftime("%Y-%m-%d %H:%M")
        )

    def reject(self, command: ManageRequestCommand) -> ManageRequestResult:
        """
        Finalizes a request as REJECTED and notifies the customer.
        
        Sets the request status to REJECTED and sends a declination message.

        Args:
            

        Raises:
            ValueError: If the request ID is invalid or not in a PENDING state.
            NotificationDeliveryError: If the WhatsApp message fails to send.
        
        Returns:

        """
        req = self._get_request(command.request_id)
        final_text = command.override_text or req.generated_response

        try:
            self.whatsapp_Port.send_text_message(req.wa_id, final_text)
        except Exception as e:
            logging.error(f"Error sending WhatsApp message on request {req.uid} rejection: {e}")

        req.reject()
        req.generated_response = final_text
        self.repo.save(req)
        
        return ManageRequestResult(
            request_id=str(req.uid),
            customer=req.customer_name,
            wa_id=req.wa_id,
            new_status=req.status.value,
            message=f"Pedido rejeitado e {req.wa_id} ({req.customer_name}) notificado.",
            processed_at=req.processed_at.strftime("%Y-%m-%d %H:%M")
        )

    def _get_request(self, request_id: str) -> Request:
        """
        Helper method to retrieve a Request entity or fail early.
        
        Args:
            request_id (str): UUID string of the request.
            
        Returns:
            Request: The domain entity if found.
        """
        req = self.repo.get_by_id(uuid.UUID(request_id))
        if not req:
            raise ValueError("Request not found.")
        return req