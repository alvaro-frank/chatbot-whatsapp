import uuid
from app.domain.ports import WhatsAppProvider, IRequestRepository

class ManageRequestActionUseCase:
    """
    Use Case for executing administrative decisions on customer requests.
    
    This service orchestrates the transition of requests from PENDING to final 
    states (APPROVED/REJECTED) and manages the subsequent communication via WhatsApp.
    """
    def __init__(self, repo: IRequestRepository, whatsapp_provider: WhatsAppProvider):
        """
        Initializes the use case with persistence and communication dependencies.
        
        Args:
            repo (IRequestRepository): Repository to fetch and update Request entities.
            whatsapp_provider (WhatsAppProvider): Provider to dispatch final notifications.
        """
        self.repo = repo
        self.whatsapp_provider = whatsapp_provider

    def approve(self, request_id: str, override_text: str = None) -> None:
        """
        Finalizes a request as APPROVED and notifies the customer.
        
        This method updates the domain entity state, sets the final response text 
        (allowing for manual edits), dispatches the message, and persists the change.

        Args:
            request_id (str): The unique ID of the request to approve.
            override_text (str, optional): A manually edited version of the AI response.

        Raises:
            ValueError: If the request ID is invalid or the record doesn't exist.
            NotificationDeliveryError: If the WhatsApp message fails to send.
        """
        req = self._get_request(request_id)
        final_text = override_text or req.generated_response

        self.whatsapp_provider.send_text_message(req.wa_id, final_text)

        req.approve()
        req.generated_response = final_text
        self.repo.save(req)

    def reject(self, request_id: str, override_text: str = None) -> None:
        """
        Finalizes a request as REJECTED and notifies the customer.
        
        Sets the request status to REJECTED and sends a declination message.

        Args:
            request_id (str): The unique ID of the request to reject.
            override_text (str, optional): A custom rejection reason. Defaults to a standard message.

        Raises:
            ValueError: If the request ID is invalid or not in a PENDING state.
        """
        req = self._get_request(request_id)
        final_text = override_text or "O seu pedido não pôde ser processado."

        self.whatsapp_provider.send_text_message(req.wa_id, final_text)

        req.reject()
        req.generated_response = final_text
        self.repo.save(req)

    def _get_request(self, request_id: str):
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