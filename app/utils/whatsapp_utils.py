import logging
from flask import current_app, jsonify
import json
import requests
import google.generativeai as genai

# from app.services.openai_service import generate_response
import re


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

"""
def generate_response(response):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    num1 = random.randint(1, 1000)
    num2 = random.randint(1, 1000)
    soma = num1 + num2

    return f"{dt_string} -> {num1} + {num2} = {soma}"
"""

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
    api_key = current_app.config["GEMINI_API_KEY"]
    if not api_key:
        logging.error("❌ ERRO CRÍTICO: GEMINI_API_KEY não encontrada nas configurações!")
        return None
    else:
        # Imprime os primeiros 5 caracteres só para confirmar que carregou algo
        logging.info(f"🔑 API Key carregada: {api_key[:5]}...")
    
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel("gemini-flash-latest")
    
    prompt = f"""
    És um assistente de CRM de uma contabilidade experiente e prestável.
    
    1. Analisa a mensagem do cliente: "{message_body}"
    2. Extrai a intenção ("alterar_nif" ou "outro") e o NIF se existir.
    3. Gera uma resposta curta, educada e profissional para o cliente.
       - INCLUI SEMPRE o nome "{user_name}" na resposta para ser mais pessoal.
       - Se for "alterar_nif" com NIF válido: Confirma que a alteração foi efetuada com sucesso na ficha de cliente.
       - Se for "alterar_nif" sem NIF: Pede o número educadamente.
       - Se for "outro": Diz que um contabilista vai analisar o pedido.

    INSTRUÇÕES DE IDIOMA:
    1. Identificar o idioma em que o cliente escreveu (Português, Inglês, Espanhol, Francês, etc.).
    2. A resposta gerada no campo "message_to_customer" DEVE ser obrigatoriamente nesse mesmo idioma.
    3. Se o idioma for ambíguo, usa Português de Portugal como padrão.
    
    O cliente chama-se: "{user_name}".
    Mensagem do cliente: "{message_body}"
    
    Responde APENAS com um JSON neste formato:
    {{
        "intent": "alterar_nif" ou "outro",
        "nif": "número extraído ou null se não houver",
        "confidence": "alto", "medio" ou "baixo",
        "response_draft": "O texto da resposta sugerida aqui..."
    }}

    Mensagem do cliente: "{message_body}"
    """
    
    try:
        response = model.generate_content(prompt)
        
        logging.info(f"🤖 Resposta Bruta do Gemini: {response.text}")
        
        text_response = response.text.strip().replace('```json', '').replace('```', '')
        data = json.loads(text_response)
        
        logging.info(f"✅ JSON Parseado: {data}")
        
        return data
    except Exception as e:
        logging.error(f"❌ ERRO no extract_information: {str(e)}")

        if 'response' in locals() and hasattr(response, 'prompt_feedback'):
            logging.error(f"⚠️ Feedback de Segurança: {response.prompt_feedback}")
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

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    ai_context = extract_information(message_body, name)
    
    final_response = "Desculpe, não consegui processar o seu pedido neste momento."
    
    if ai_context:
        generated_text = ai_context.get("response_draft")
        
        if generated_text:
            final_response = generated_text
            
            if ai_context.get("nif"):
                logging.info(f"NIF detetado: {ai_context.get('nif')}")

    data = get_text_message_input(current_app.config["RECIPIENT_WAID"], final_response)
    send_message(data)


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
