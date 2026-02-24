import logging
from datetime import datetime
from app.domain.interfaces import WhatsAppProvider
from app.infrastructure.persistence_adapters.request_repository import RequestRepository
from app.dtos.dtos import IncomingMessageDTO, AIAnalysisDTO, RequestDTO
from app.commands.command_factory import CommandFactory
from app.domain.entities import Request
import uuid

class RequestService:
    """

    """
    def __init__(self, repo: RequestRepository, whatsapp_provider: WhatsAppProvider):
        """

        """
        self.repo = repo
        self.whatsapp_provider = whatsapp_provider

    def handle_ai_analysis(self, message: IncomingMessageDTO, analysis: AIAnalysisDTO):
        """

        """
        if analysis.intent in ["alterar_nif", "alterar_morada"]:
            new_request = Request(
                wa_id=message.wa_id,
                customer_name=message.sender_name,
                intent=analysis.intent,
                user_input=message.message_body,
                field_value=analysis.field_value,
                generated_response=analysis.response_draft,
            )
            self.repo.save(new_request)
            logging.info(f"Service request created for intent: {analysis.intent}")

    def list_active_requests(self) -> list[RequestDTO]:
        """

        """
        requests = self.repo.get_all_pending()

        output = []
        for r in requests:
            command = CommandFactory.get_command(r.intent)
            simulation_data = command.execute(r)
            
            output.append(RequestDTO(
                id=str(r.uid),
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

    def process_approval(self, request_id: str, override_text: str = None) -> bool:
        """
        
        """
        req = self.repo.get_by_id(uuid.UUID(request_id))
        if not req:
            raise ValueError("Request not found")

        final_text = override_text or req.generated_response
        
        success = self.whatsapp_provider.send_text_message(
            recipient_id=req.wa_id,
            message_text=final_text
        )

        if success:
            req.approve()
            req.generated_response = final_text
            self.repo.save(req) 
            return True
        
        return False

    def process_rejection(self, request_id: str, override_text: str = None) -> bool:
        """
        
        """
        req = self.repo.get_by_id(uuid.UUID(request_id))
        if not req:
             raise ValueError("Request not found")

        final_text = override_text or "O seu pedido não pôde ser processado."
        
        self.whatsapp_provider.send_text_message(req.wa_id, final_text)

        req.reject() 
        req.generated_response = final_text
        
        self.repo.save(req)
        return True