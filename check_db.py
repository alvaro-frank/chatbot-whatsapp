from app import create_app
from app.extensions import db
from app.models import ServiceRequest

# Criar a app para ter acesso à configuração da BD
app = create_app()

def ver_pedidos():
    with app.app_context():
        # 1. Buscar todos os pedidos com status PENDING
        pedidos = ServiceRequest.query.filter_by(status='PENDING').all()
        
        print(f"\n📋 ENCONTREI {len(pedidos)} PEDIDOS PENDENTES:\n")
        print("-" * 50)
        
        for p in pedidos:
            print(f"🆔 ID: {p.id}")
            print(f"👤 Cliente: {p.customer_name} ({p.wa_id})")
            print(f"🎯 Intenção: {p.intent}")
            print(f"🔢 Valor do Campo: {p.field_value}")
            print(f"🤖 Resposta Sugerida: {p.generated_response}")
            print(f"📅 Data: {p.created_at}")
            print("-" * 50)

if __name__ == "__main__":
    ver_pedidos()