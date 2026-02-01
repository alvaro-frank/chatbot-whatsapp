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
from app.services.ai_service import AIService

class WhatsAppService:
    def __init__(self):
        self.repo = RequestRepository()
        self.ai_service = AIService()

    def process_incoming_message(self, body: dict):
        """
        Main entry point for processing a webhook event.
        """
        try:
            # 1. Parsing
            entry = body["entry"][0]["changes"][0]["value"]
            contact = entry["contacts"][0]
            message = entry["messages"][0]

            wa_id = contact["wa_id"]
            name = contact["profile"]["name"]
            first_name = name.split()[0]
            message_body = message["text"]["body"]

            # 2. AI Analysis
            ai_context = self.ai_service.analyze_message(message_body, first_name)
            
            if not ai_context:
                logging.error("Failed to get AI context. Skipping.")
                return

            intent = ai_context.get("intent")
            
            if intent == "outro":
                logging.info(f"Ignored 'outro' intent from {name}")
                return

            # 3. Persistence
            new_request = ServiceRequest(
                wa_id=wa_id,
                customer_name=name,
                intent=intent,
                field_value=ai_context.get("field_value"),
                user_input=message_body,
                generated_response=ai_context.get("response_draft"),
                status='PENDING' 
            )
            
            self.repo.add(new_request)
            logging.info(f"✅ Pedido guardado via Service: {new_request.id}")

        except KeyError as e:
            logging.error(f"⚠️ Invalid Message Format: {e}")
        except Exception as e:
            logging.error(f"❌ Error processing message: {e}")