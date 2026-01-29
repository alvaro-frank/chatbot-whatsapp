import logging
from flask import current_app, jsonify
import json
import requests
from groq import Groq
import re

from app.extensions import db
from app.models import ServiceRequest

def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response

def extract_information(message_body, user_name):
    """
    Usa a Groq (Llama 3) para extrair a intenção e gerar a resposta.
    """
    api_key = current_app.config.get("GROQ_API_KEY")
    if not api_key:
        logging.error("GROQ_API_KEY não configurada.")
        return None

    client = Groq(api_key=api_key)
    
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
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message_body}
            ],
            model="llama-3.3-70b-versatile", # Modelo muito inteligente e gratuito
            
            # Isto obriga o modelo a responder APENAS JSON (Super Importante)
            response_format={"type": "json_object"}, 
            
            temperature=0
        )

        # Processar a resposta
        response_content = completion.choices[0].message.content
        data = json.loads(response_content)
        return data

    except Exception as e:
        logging.error(f"Erro na Groq: {e}")
        return None

def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
    first_name = name.split()[0]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    ai_context = extract_information(message_body, first_name)
    
    if ai_context:
        intent = ai_context.get("intent")
        nif = ai_context.get("field_value")
        generated_msg = ai_context.get("response_draft")

        # 2. CRIAR REGISTO NA BASE DE DADOS (PENDENTE)
        try:
            new_request = ServiceRequest(
                wa_id=wa_id,
                customer_name=name,
                intent=intent,
                field_value=nif,
                generated_response=generated_msg,
                status='PENDING' 
            )
            db.session.add(new_request)
            db.session.commit()
            logging.info(f"✅ Pedido guardado na BD com ID: {new_request.id}")
            
        except Exception as e:
            logging.error(f"❌ Erro ao gravar na BD: {e}")
            db.session.rollback()
            return # Sai se der erro na BD
    else:
        logging.error("Falha ao obter contexto da IA.")


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
