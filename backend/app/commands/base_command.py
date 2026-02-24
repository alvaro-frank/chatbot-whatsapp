from abc import ABC, abstractmethod

class BaseSimulationCommand(ABC):
    """
    Abstract interface for system simulation logic.
    
    Implementing classes define how a specific intent (e.g., 'alterar_nif') 
    would affect the system. This is used to provide a 'preview' to 
    administrators before a request is officially approved.
    """
    @abstractmethod
    def execute(self, request_model) -> dict:
        """
        Executes the simulation logic and returns the results.
        
        Args:
            request_model (Request): The domain entity containing the customer's data.
            
        Returns:
            dict: A structured dictionary containing the 'before' and 'after' state 
                  of the simulated data, or any relevant system metadata.
        """
        pass