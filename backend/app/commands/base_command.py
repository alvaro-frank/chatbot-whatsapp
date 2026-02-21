# ==============================================================================
# FILE: app/commands/base_command.py
# DESCRIPTION: Abstract interface for simulation commands.
# ==============================================================================

from abc import ABC, abstractmethod

class BaseSimulationCommand(ABC):
    @abstractmethod
    def execute(self, request_model) -> dict:
        """
        Executes the simulation logic and returns a dictionary.
        """
        pass