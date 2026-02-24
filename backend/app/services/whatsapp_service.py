import logging
from app.domain.interfaces import LLMProvider, WhatsAppProvider
from app.services.request_service import RequestService
from app.dtos.dtos import IncomingMessageDTO, AIAnalysisDTO

class WhatsAppService:
    """
    Orchestrator service responsible for the end-to-end processing of messages.
    
    Acting as a 'Maestro' in the Application Layer, it ensures that incoming 
    data is analyzed by the AI and subsequently handled by the Domain Layer 
    according to defined business rules.
    """
    def __init__(
        self, 
        llm_provider: LLMProvider, 
        whatsapp_provider: WhatsAppProvider,
        request_service: RequestService
    ):
        """
        Initializes the service using Dependency Injection (Inversion of Control).
        
        Args:
            llm_provider (LLMProvider): The interface for AI/NLP processing.
            whatsapp_provider (WhatsAppProvider): The interface for messaging transport.
            request_service (RequestService): The domain service for business logic.
        """
        self.llm_provider = llm_provider
        self.whatsapp_provider = whatsapp_provider
        self.request_service = request_service

    def process_incoming_message(self, message_dto: IncomingMessageDTO):
        """
        Executes the high-level orchestration flow for a single messaging event.
        
        Orchestration Steps:
        1. AI Interpretation: Sends raw text to the LLM to extract intent/entities.
        2. Domain Delegation: Passes the analysis to the RequestService to 
           determine if a database record or specific business action is required.
        3. Error Handling: Captures failures in the pipeline to prevent 
           cascading crashes in the Webhook.
        
        Args:
            message_dto (IncomingMessageDTO): The sanitized input message data.
        """
        logging.info(f"Iniciando processamento para: {message_dto.wa_id}")

        try:
            analysis: AIAnalysisDTO = self.llm_provider.analyze_message(
                message_body=message_dto.message_body,
                user_name=message_dto.first_name
            )

            self.request_service.handle_ai_analysis(message_dto, analysis)
        except Exception as e:
            logging.error(f"Erro crítico no orquestrador WhatsAppService: {e}")