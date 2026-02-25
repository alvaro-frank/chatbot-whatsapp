from functools import wraps
from flask import current_app, jsonify, request
import logging
import hashlib
import hmac


def validate_signature(payload, signature):
    """
    Validates the SHA256 signature provided by Meta using HMAC.
    
    This ensures the request actually originated from Meta and has not been 
    tampered with during transit. It compares a locally generated hash 
    with the one sent in the request header.

    Args:
        payload (str): The raw request body (JSON string).
        signature (str): The hex-encoded signature extracted from the header.

    Returns:
        bool: True if signatures match, False otherwise.
    """
    secret = current_app.config.get("APP_SECRET")
    if not secret:
        logging.error("❌ APP_SECRET is not configured.")
        return False

    expected_signature = hmac.new(
        bytes(secret, "latin-1"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


def signature_required(f):
    """
    Decorator to protect routes by verifying the X-Hub-Signature-256 header.
    
    This middleware-style wrapper intercepts the request before it reaches 
    the controller. If the signature is missing or invalid, it returns a 
    403 Forbidden response.

    Args:
        f (function): The view function to be decorated.

    Returns:
        function: The decorated function that includes signature validation logic.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        header_signature = request.headers.get("X-Hub-Signature-256", "")
        
        # Robust parsing of the 'sha256=' prefix
        if not header_signature or not header_signature.startswith("sha256="):
            logging.warning("⚠️ Missing or invalid signature format in headers.")
            return jsonify({"status": "error", "message": "Signature missing"}), 403

        # Extract signature after 'sha256='
        signature = header_signature.replace("sha256=", "")
        
        if not validate_signature(request.data.decode("utf-8"), signature):
            logging.error(f"❌ Signature verification failed for IP: {request.remote_addr}")
            return jsonify({"status": "error", "message": "Invalid signature"}), 403
            
        return f(*args, **kwargs)

    return decorated_function
