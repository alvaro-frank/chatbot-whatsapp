# ==============================================================================
# FILE: app/services/whatsapp_service.py
# DESCRIPTION: Orchestrates the incoming WhatsApp message flow.
#              1. Parses raw webhook data.
#              2. Calls AIService for analysis.
#              3. Saves result via RequestRepository.
# ==============================================================================

import logging
from app.models import ServiceRequest
from app.repositories.request_repository import RequestRepository
from app.services.ai_service import BaseLLMService
from app.dtos.whatsapp_dto import IncomingMessageDTO

class WhatsAppService:
    def __init__(self, repo: RequestRepository, ai_service: BaseLLMService):
        self.repo = repo
        self.ai_service = ai_service

    def process_incoming_message(self, message_dto: IncomingMessageDTO):
        """
        Main entry point for processing a webhook event.
        """
        try:
            # 1. AI Analysis
            ai_context = self.ai_service.analyze_message(
                message_dto.message_body, 
                message_dto.first_name
            )
            
            if not ai_context:
                logging.error("Failed to get AI context. Skipping.")
                return

            intent = ai_context.get("intent")
            
            if intent == "outro":
                logging.info(f"Ignored 'outro' intent from {message_dto.sender_name}")
                return

            # 2. Persistence
            new_request = ServiceRequest(
                wa_id=message_dto.wa_id,
                customer_name=message_dto.sender_name,
                intent=intent,
                field_value=ai_context.get("field_value"),
                user_input=message_dto.message_body,
                generated_response=ai_context.get("response_draft"),
                status='PENDING' 
            )
            
            self.repo.add(new_request)
            logging.info(f"✅ Pedido guardado: {new_request.id}")

        except KeyError as e:
            logging.error(f"⚠️ Invalid Message Format: {e}")
        except Exception as e:
            logging.error(f"❌ Error processing message: {e}")