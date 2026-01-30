from flask import Blueprint, jsonify
from app.extensions import db
from app.models import ServiceRequest
from app.utils.whatsapp_utils import send_message, get_text_message_input
from flask import request

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

@admin_blueprint.route("/requests", methods=["GET"])
def get_pending_requests():
    try:
        expiration_limit = datetime.utcnow() - timedelta(hours=24)
        
        deleted_count = ServiceRequest.query.filter(
            ServiceRequest.status == 'PENDING',
            ServiceRequest.created_at < expiration_limit
        ).delete()
        
        if deleted_count > 0:
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro na limpeza automática: {e}")
        
    requests = ServiceRequest.query.filter_by(status='PENDING').all()
    
    output = []
    for r in requests:
        simulation_data = {}
        if r.intent == "alterar_nif":
            simulation_data = {
                "action": r.intent,
                "target_table": "TABELA_CLIENTES_CRM",
                "parameters": {
                    "value": r.field_value,
                },
                "where": {
                    "client_id": "ID do cliente associado ao CRM"
                }
            }
        
        output.append({
            "id": r.id,
            "customer": r.customer_name,
            "wa_id": r.wa_id,
            "intent": r.intent,
            "field_value": r.field_value,
            "user_input": r.user_input,
            "response_text": r.generated_response,
            "date": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "system_simulation": simulation_data
        })
    
    return jsonify(output), 200

@admin_blueprint.route("/requests/<int:request_id>/approve", methods=["POST"])
def approve_request(request_id):
    req = ServiceRequest.query.get_or_404(request_id)

    if req.status != 'PENDING':
        return jsonify({"error": "Este pedido já foi processado"}), 400
    
    body = request.get_json(silent=True) or {}
    final_text = body.get('response_text', req.generated_response)

    req.status = 'APPROVED'
    req.generated_response = final_text
    
    print(f"🔄 A ATUALIZAR NIF DO CLIENTE {req.customer_name} PARA {req.field_value}...")

    data = get_text_message_input(req.wa_id, req.generated_response)
    response = send_message(data)

    if response.status_code == 200:
        db.session.commit()
        return jsonify({"message": "Aprovado e enviado com sucesso!"}), 200
    else:
        return jsonify({"error": "Falha ao enviar mensagem WhatsApp"}), 500

@admin_blueprint.route("/requests/<int:request_id>/reject", methods=["POST"])
def reject_request(request_id):
    req = ServiceRequest.query.get_or_404(request_id)
    
    if req.status != 'PENDING':
        return jsonify({"error": "Este pedido já foi processado"}), 400
    body = request.get_json(silent=True) or {}
    final_text = body.get('response_text', "O seu pedido não pôde ser processado. Por favor contacte o suporte.")
    req.status = 'REJECTED'
    req.generated_response = final_text
    try:
        data = get_text_message_input(req.wa_id, final_text)
        send_message(data)
    except Exception as e:
        print(f"Erro ao enviar mensagem de rejeição: {e}")

    db.session.commit()
    
    return jsonify({"message": "Pedido rejeitado e cliente notificado."}), 200