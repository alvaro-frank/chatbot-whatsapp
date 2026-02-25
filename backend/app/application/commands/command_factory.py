from app.application.commands.simulation_commands import AlterarNifCommand, AlterarMoradaCommand, DefaultSimulationCommand

class CommandFactory:
    """
    Registry and Factory for simulation commands.
    
    This class implements the Factory Pattern to decouple the caller from 
    specific command implementations. It maps string-based intents 
    (from the AI layer) to their respective simulation logic.
    """
    _COMMANDS = {
        "alterar_nif": AlterarNifCommand,
        "alterar_morada": AlterarMoradaCommand,
    }
    
    @classmethod
    def is_actionable_intent(cls, intent: str) -> bool:
        """
        Validates if the provided intent has a specialized command implementation.

        This is used by the orchestration layer to determine if the system should 
        execute a specific business logic flow or fall back to a general response.

        Args:
            intent (str): The intent slug identified by the LLM.

        Returns:
            bool: True if the intent is registered in the factory, False otherwise.
        """
        return intent in cls._COMMANDS

    @staticmethod
    def get_command(intent: str):
        """
        Retrieves the appropriate command instance for a given intent.
        
        If the intent is not recognized or does not have a specialized 
        simulation, it returns a DefaultSimulationCommand to ensure 
        system stability.

        Args:
            intent (str): The intent slug identified by the LLM.

        Returns:
            BaseSimulationCommand: A concrete implementation of the simulation logic.
        """
        command_class = CommandFactory._COMMANDS.get(intent, DefaultSimulationCommand)
        return command_class()