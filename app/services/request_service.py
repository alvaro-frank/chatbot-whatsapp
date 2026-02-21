# ==============================================================================
# FILE: app/services/request_service.py
# DESCRIPTION: Core Domain Service responsible for the ServiceRequest lifecycle.
#              Orchestrates business validation, persistence via repositories,
#              simulation logic via Command Pattern, and outbound notifications.
# ==============================================================================

import logging
from datetime import datetime
from app.domain.interfaces import WhatsAppProvider
from app.repositories.request_repository import RequestRepository
from app.dtos.dtos import IncomingMessageDTO, AIAnalysisDTO, ServiceRequestDTO
from app.commands.command_factory import CommandFactory
from app.models import ServiceRequest

class RequestService:
    """
    Domain Service handling administrative workflows for ServiceRequests.
    
    This service acts as the intermediary between the API controllers and the 
    domain logic. It ensures that data remains consistent during approval 
    workflows and handles the transformation between SQL models and DTOs.
    """
    def __init__(self, repo: RequestRepository, whatsapp_provider: WhatsAppProvider):
        """
        Initializes the service with required infrastructure dependencies.
        
        Args:
            repo (RequestRepository): Persistence layer for ServiceRequest entities.
            whatsapp_provider (WhatsAppProvider): Interface for external notifications.
        """
        self.repo = repo
        self.whatsapp_provider = whatsapp_provider

    def handle_ai_analysis(self, message: IncomingMessageDTO, analysis: AIAnalysisDTO):
        """
        Applies business filtering to AI analysis results.
        
        Evaluates the detected intent and determines if the interaction should 
        be escalated to a formal ServiceRequest in the database.
        
        Args:
            message (IncomingMessageDTO): The original message context.
            analysis (AIAnalysisDTO): Intelligence extracted by the LLM.
        """
        if analysis.intent in ["alterar_nif", "alterar_morada"]:
            new_request = ServiceRequest(
                wa_id=message.wa_id,
                customer_name=message.sender_name,
                intent=analysis.intent,
                user_input=message.message_body,
                field_value=analysis.field_value,
                generated_response=analysis.response_draft,
                status='PENDING'
            )
            self.repo.add(new_request)
            logging.info(f"Service request created for intent: {analysis.intent}")

    def list_active_requests(self) -> list[ServiceRequestDTO]:
        """
        Retrieves pending requests and enriches them with simulation data.
        
        This method uses the Command Pattern to execute intent-specific simulations 
        (e.g., checking current NIF in a legacy system) before returning 
        the data to the dashboard.
        
        Returns:
            list[ServiceRequestDTO]: A collection of validated, display-ready objects.
        """
        requests = self.repo.get_all_pending()

        output = []
        for r in requests:
            command = CommandFactory.get_command(r.intent)
            simulation_data = command.execute(r)
            
            output.append(ServiceRequestDTO(
                id=r.id,
                customer=r.customer_name,
                wa_id=r.wa_id,
                intent=r.intent,
                field_value=r.field_value,
                user_input=r.user_input,
                response_text=r.generated_response,
                date=r.created_at.strftime("%Y-%m-%d %H:%M"),
                system_simulation=simulation_data
            ))
        return output

    def process_approval(self, request_id: int, override_text: str = None) -> bool:
        """
        Finalizes a request and dispatches the final response to the user.
        
        Transitions the request state to 'APPROVED' and synchronizes the 
        decision with the user via WhatsApp.
        
        Args:
            request_id (int): Database identifier of the target request.
            override_text (str, optional): Custom message text from the admin.
            
        Returns:
            bool: Success status of the outbound notification.
            
        Raises:
            ValueError: If the request state is not 'PENDING'.
        """
        req = self.repo.get_by_id(request_id)

        if req.status != 'PENDING':
            raise ValueError("Request already processed")

        final_text = override_text or req.generated_response

        success = self.whatsapp_provider.send_text_message(
            recipient_id=req.wa_id,
            message_text=final_text
        )

        if success:
            req.status = 'APPROVED'
            req.generated_response = final_text
            req.processed_at = datetime.utcnow()
            self.repo.save()
            return True
        
        return False

    def process_rejection(self, request_id: int, override_text: str = None) -> bool:
        """
        Rejects a request and notifies the user of the decision.
        
        Transitions the request state to 'REJECTED'. Notification failure 
        does not roll back the database state.
        
        Args:
            request_id (int): Database identifier of the target request.
            override_text (str, optional): Custom rejection reason.
        """
        req = self.repo.get_by_id(request_id)

        if req.status != 'PENDING':
             raise ValueError("Request already processed")

        final_text = override_text or "O seu pedido não pôde ser processado."
        
        self.whatsapp_provider.send_text_message(req.wa_id, final_text)

        req.status = 'REJECTED'
        req.generated_response = final_text
        req.processed_at = datetime.utcnow()
        self.repo.save()
        return True