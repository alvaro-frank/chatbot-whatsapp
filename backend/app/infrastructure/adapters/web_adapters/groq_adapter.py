import json
import logging
from groq import Groq
from app.domain.ports.ports import LLMPort
from app.application.dtos.results import AIAnalysisResult
from app.domain.entities.entities import MessageAnalysis

class GroqAdapter(LLMPort):
    """
    Adapter implementation for the Groq Cloud API.
    
    This class handles the complexity of communicating with Groq's inference 
    engine, managing prompts, and enforcing structured JSON outputs.
    """
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        """
        Initializes the Groq client with necessary authentication.
        
        Args:
            api_key (str): The secret API key from Groq Cloud.
            model (str): The specific model ID to use for inference. 
                         Defaults to Llama 3.3 70B for high-precision extraction.
        
        Raises:
            ValueError: If the api_key is missing or null.
        """
        if not api_key:
            raise ValueError("Groq API Key is required for GroqAdapter.")
        self.client = Groq(api_key=api_key)
        self.model = model

    def analyze_message(self, message_body: str, user_name: str) -> MessageAnalysis:
        """
        Sends the user message to Groq for NLU (Natural Language Understanding) processing.
        
        This method orchestrates the full analysis flow:
        1. Generates a contextual system prompt.
        2. Calls the Groq Chat Completion API with JSON mode enabled.
        3. Validates the raw JSON output against the AIAnalysisResult schema.
        4. Maps the validated DTO to a Domain Entity (MessageAnalysis).

        Args:
            message_body (str): The raw text sent by the customer.
            user_name (str): The name of the customer for personalized AI responses.

        Returns:
            MessageAnalysis: A domain-layer entity containing the structured results.

        Raises:
            ConnectionError: If the API call fails or the response cannot be parsed.
        """
        prompt = self._get_system_prompt(user_name, message_body)
        
        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message_body}
                ],
                model=self.model,
                response_format={"type": "json_object"},
                temperature=0
            )
            
            response_content = completion.choices[0].message.content
            
            validated_dto = AIAnalysisResult.model_validate_json(response_content)
            
            return MessageAnalysis(
                detected_language=validated_dto.detected_language,
                intent=validated_dto.intent,
                field_value=validated_dto.field_value,
                confidence_score=validated_dto.confidence_score,
                response_draft=validated_dto.response_draft
            )

        except Exception as e:
            logging.error(f"❌ Groq Adapter Error: {e}")
            raise ConnectionError(f"Failed to get analysis from Groq: {e}")

    def _get_system_prompt(self, user_name: str, message_body: str) -> str:
        """
        Constructs the internal system prompt that defines the bot's behavior.
        
        This is the 'brain' of the adapter. It defines intent categories, 
        extraction rules, and formatting constraints.
        
        Args:
            user_name (str): Name of the client for personalized drafting.
            message_body (str): Message content for context.
            
        Returns:
            str: The full system prompt to be sent to the LLM.
        """
        
        prompt = f"""
        You are an advanced CRM Virtual Assistant. Your goal is to process incoming messages with high precision, extracting intent, entities, and generating human-like responses.

        USER CONTEXT:
        - Client Name: "{user_name}"
        - Incoming Message: "{message_body}"

        CORE TASKS:
        1. LANGUAGE DETECTION: Identify the ISO language code (pt, en, es, etc.).
        2. INTENT CLASSIFICATION: Categorize the request into the most appropriate intent.
        3. ENTITY EXTRACTION: Identify the primary value related to the intent (e.g., NIF, Address, Date).
        4. RESPONSE GENERATION: Draft a response matching the detected language and tone.

        BUSINESS LOGIC & INTENTS:
        - "alterar_nif": Used when the user wants to update their Tax ID. 
            * If a number is found, confirm the reception for analysis.
            * If missing, ask for it politely.
        - "alterar_morada": Used for address updates.
            * If a number is found, confirm the reception for analysis.
            * If missing, ask for it politely.
        - "pedido_informacao": General questions about services.
        - "outro": Any request that does not fit the specific categories above.

        STRICT GUIDELINES:
        - PERSONALIZATION: Always address the user as "{user_name}".
        - LANGUAGE PARITY: The "response_draft" MUST be in the same language as the "Incoming Message".
        - JSON ONLY: Output must be a valid JSON object. No prose.

        OUTPUT FORMAT:
        {{
            "detected_language": "string",
            "intent": "string",
            "field_value": "string or null",
            "confidence_score": float (0.0 to 1.0),
            "response_draft": "string"
        }}
        """
        
        return prompt