# ==============================================================================
# FILE: app/services/ai_service.py
# DESCRIPTION: Handles all interactions with the LLM.
#              Responsible for intent classification and entity extraction.
# ==============================================================================

import json
import logging
from flask import current_app
from groq import Groq
from app.services.base_llm_service import BaseLLMService

class AIService(BaseLLMService):
    def __init__(self):
        self.api_key = current_app.config.get("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            logging.warning("⚠️ GROQ_API_KEY not found. AI features will be disabled.")

    def analyze_message(self, message_body: str, user_name: str) -> dict:
        """
        Sends the user message to the LLM and parses the JSON response.
        
        Args:
            message_body (str): The text sent by the user.
            user_name (str): The user's first name for context.
            
        Returns:
            dict: Structured data (intent, nif, response_draft) or None if failed.
        """
        if not self.client:
            return None

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
        
        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message_body}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}, 
                temperature=0
            )
            response_content = completion.choices[0].message.content
            return json.loads(response_content)

        except Exception as e:
            logging.error(f"❌ Groq API Error: {e}")
            return None