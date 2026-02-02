# ==============================================================================
# FILE: app/services/request_service.py
# DESCRIPTION: Contains the business logic for managing ServiceRequests.
#              Orchestrates database updates and external API calls (WhatsApp).
# ==============================================================================

from datetime import datetime, timedelta
from app.repositories.request_repository import RequestRepository
from app.utils.whatsapp_utils import send_message, get_text_message_input

class RequestService:
    """
    Service layer handling the lifecycle of ServiceRequests (clean, approve, reject).
    """

    def __init__(self, repo: RequestRepository):
        self.repo = RequestRepository()

    def list_active_requests(self):
        """
        Performs lazy cleanup of expired requests (older than 24h) 
        and returns the list of currently valid pending requests.
        
        Returns:
            list[dict]: A list of dictionaries ready for JSON response.
        """

        # 1. Fetch Data
        requests = self.repo.get_all_pending()

        # 2. Transform Data (DTO pattern)
        output = []
        for r in requests:
            simulation_data = {}
            if r.intent == "alterar_nif":
                simulation_data = {
                    "action": r.intent,
                    "target_table": "TABELA_CLIENTES_CRM",
                    "parameters": {"value": r.field_value},
                    "where": {"client_id": "CRM_ID_PLACEHOLDER"}
                }
            
            output.append({
                "id": r.id,
                "customer": r.customer_name,
                "wa_id": r.wa_id,
                "intent": r.intent,
                "field_value": r.field_value,
                "user_input": r.user_input,
                "response_text": r.generated_response,
                "date": r.created_at.strftime("%Y-%m-%d %H:%M"),
                "system_simulation": simulation_data
            })
        return output

    def process_approval(self, request_id: int, response_text: str = None):
        """
        Approves a request, updates the status, and sends a WhatsApp confirmation.
        
        Args:
            request_id (int): The ID of the request to approve.
            response_text (str): Optional override for the response message.
            
        Returns:
            bool: True if successful.
            
        Raises:
            ValueError: If request is not in PENDING state.
            Exception: If WhatsApp sending fails.
        """
        req = self.repo.get_by_id(request_id)

        if req.status != 'PENDING':
            raise ValueError("Request already processed")

        # Business Logic
        final_text = response_text or req.generated_response
        req.status = 'APPROVED'
        req.generated_response = final_text

        # External Integration
        data = get_text_message_input(req.wa_id, req.generated_response)
        response = send_message(data)

        if response.status_code == 200:
            self.repo.save()
            return True
        else:
            raise Exception("Failed to send WhatsApp message")

    def process_rejection(self, request_id: int, response_text: str = None):
        """
        Rejects a request and notifies the client via WhatsApp.
        
        Args:
            request_id (int): The ID of the request to reject.
            response_text (str): Optional rejection reason.
            
        Returns:
            bool: True if processed successfully.
        """
        req = self.repo.get_by_id(request_id)

        if req.status != 'PENDING':
             raise ValueError("Request already processed")

        final_text = response_text or "O seu pedido não pôde ser processado."
        req.status = 'REJECTED'
        req.generated_response = final_text

        # External Integration (Fail-safe)
        try:
            data = get_text_message_input(req.wa_id, final_text)
            send_message(data)
        except Exception as e:
            print(f"Warning: Failed to send rejection message: {e}")

        self.repo.save()
        return True