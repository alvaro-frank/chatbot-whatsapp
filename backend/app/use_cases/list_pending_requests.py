import logging
from app.infrastructure.persistence_adapters.request_repository import IRequestRepository
from app.commands.command_factory import CommandFactory
from app.dtos.dtos import RequestDTO
from typing import List

class ListPendingRequestsUseCase:
    """
    Use Case responsible for retrieving and preparing pending requests for the admin UI.
    
    This class orchestrates the retrieval of 'PENDING' requests from the repository 
    and enrichment of that data with system simulations provided by the Command layer.
    """
    
    def __init__(self, repo: IRequestRepository):
        """
        Initializes the use case with a concrete repository implementation.
        
        Args:
            repo (IRequestRepository): The repository used to query domain entities.
        """
        self.repo = repo

    def execute(self) -> List[RequestDTO]:
        """
        Retrieves all pending requests and transforms them into DTOs with simulated effects.

        For each request, it identifies the correct Command based on the intent, 
        executes a simulation of the logic (e.g., "what would the new NIF look like in the DB?"), 
        and packages the result for frontend consumption.

        Returns:
            List[RequestDTO]: A collection of enriched data objects for the dashboard.
        """
        logging.info("Listing all pending requests for the dashboard.")

        requests = self.repo.get_all_pending()

        output = []
        for r in requests:
            try:
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
            except Exception as e:
                logging.error(f"Erro ao processar simulação para o pedido {r.uid}: {e}")
                continue

        return output