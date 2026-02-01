# ==============================================================================
# FILE: app/utils/whatsapp_utils.py
# DESCRIPTION: Shared utility functions for WhatsApp API interactions.
#              Handles message formatting and HTTP requests to Meta's Graph API.
#              Used by both WhatsAppService (Bot) and RequestService (Dashboard).
# ==============================================================================

import logging
from flask import current_app, jsonify
import requests
import json

def log_http_response(response):
    """
    Logs the status code and body of an HTTP response for debugging purposes.
    
    Args:
        response (requests.Response): The response object from the API call.
    """
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Body: {response.text}")

def get_text_message_input(recipient, text):
    """
    Formats a text message payload compliant with WhatsApp Business API.
    
    Args:
        recipient (str): The phone number of the recipient (with country code).
        text (str): The content of the text message.
        
    Returns:
        str: A JSON string ready to be sent as the HTTP request body.
    """
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    })

def send_message(data):
    """
    Executes the HTTP POST request to the WhatsApp API to send a message.
    
    Args:
        data (str): The JSON payload containing the message details.
        
    Returns:
        requests.Response: The successful API response object.
        tuple: A JSON error response and 500 status code if the request fails.
    """
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }
    
    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send message: {e}")
        return jsonify({"error": str(e)}), 500
    
    return response