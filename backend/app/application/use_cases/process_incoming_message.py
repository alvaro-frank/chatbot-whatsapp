import logging
from app.domain.ports import LLMProvider, IRequestRepository
from app.domain.entities import MessageAnalysis
from app.domain.entities import Request, ReceivedMessage
from app.application.commands.command_factory import CommandFactory
from app.application.dtos.commands import IncomingMessageCommand

class ProcessIncomingMessageUseCase:
    """
    Application Service responsible for handling new incoming messages.
    
    This Use Case orchestrates the interaction between the AI (LLMProvider) 
    and the persistence layer (Repository). It determines if a message 
    requires administrative action based on the identified intent.
    """
    def __init__(self, llm_provider: LLMProvider, repo: IRequestRepository):
        """
        Initializes the use case with necessary infrastructure abstractions.
        
        Args:
            llm_provider (LLMProvider): The adapter used to analyze natural language.
            repo (IRequestRepository): The repository used to store validated requests.
        """
        self.llm_provider = llm_provider
        self.repo = repo

    def execute(self, message_dto: IncomingMessageCommand) -> None:
        """
        Orchestrates the processing pipeline for a single received message.

        The process follows these steps:
        1. Sends message content to the LLM for analysis (intent/entities).
        2. Evaluates if the intent corresponds to a specific service request.
        3. If actionable (NIF or Address change), creates a new Request entity.
        4. Persists the Request to the database for future administrative review.

        Args:
            message (ReceivedMessage): The domain object representing the incoming message data.

        Raises:
            Exception: Re-raises any exceptions encountered during analysis or persistence for upper-layer handling.
        """
        logging.info(f"Processing message from: {message_dto.wa_id}")

        message = ReceivedMessage(
            sender_id=message_dto.wa_id,
            sender_name=message_dto.sender_name,
            content=message_dto.message_body
        )
        
        try:
            analysis: MessageAnalysis = self.llm_provider.analyze_message(
                message_body=message.content,
                user_name=message.first_name
            )

            if CommandFactory.is_actionable_intent(analysis.intent):
                command = CommandFactory.get_command(analysis.intent)
                
                simulation = command.execute(analysis)
                new_request = Request(
                    wa_id=message.sender_id,
                    customer_name=message.sender_name,
                    intent=analysis.intent,
                    user_input=message.content,
                    field_value=analysis.field_value,
                    generated_response=analysis.response_draft,
                    simulation_data=simulation
                )
                self.repo.save(new_request)
                logging.info(f"Request created: {analysis.intent}")
                
        except Exception as e:
            logging.error(f"Use Case ProcessIncomingMessage Error: {e}")
            raise e