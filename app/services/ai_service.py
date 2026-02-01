# ==============================================================================
# FILE: app/services/ai_service.py
# DESCRIPTION: Handles all interactions with the LLM (Groq).
#              Responsible for intent classification and entity extraction.
# ==============================================================================

import json
import logging
from flask import current_app
from groq import Groq

class AIService:
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
        You are an experienced and helpful CRM accounting assistant.
        
        Your Goal:
        1. Analyze the client's message: "{message_body}"
        2. Detect the language of the message (e.g., Portuguese, English, Spanish).
        3. Extract the intent and the Tax ID (NIF) if present.
        4. Generate a response IN THE SAME LANGUAGE as the client's message.

        Business Rules:
        - ALWAYS include the client's name "{user_name}" in the response to be personal.
        - Intent "alterar_nif" (Change Tax ID):
            - If valid NIF found: Confirm the update to {user_name}'s file was successful.
            - If NO NIF found: Politely ask for the new number.
        - Intent "outro" (Other):
            - State that an accountant will analyze the request manually.

        CRITICAL LANGUAGE INSTRUCTION:
        - If the user speaks English, the "response_draft" MUST be in English.
        - If the user speaks Portuguese, the "response_draft" MUST be in Portuguese.
        - Match the user's language exactly.

        Output JSON Format:
        {{
            "detected_language": "en, pt, es...",
            "intent": "alterar_nif" or "outro",
            "field_value": "extracted value or null",
            "response_draft": "The generated response text in the DETECTED LANGUAGE"
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