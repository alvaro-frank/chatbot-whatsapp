# ==============================================================================
# FILE: app/services/base_llm_service.py
# DESCRIPTION: Abstract base class for LLM providers.
#              Defines the interface for message analysis.
# ==============================================================================

from abc import ABC, abstractmethod

class BaseLLMService(ABC):
    @abstractmethod
    def analyze_message(self, message_body: str, user_name: str) -> dict:
        """
        Abstract method to analyze a message and return structured data.
        """
        pass