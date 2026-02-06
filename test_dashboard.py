import requests

BASE_URL = "http://localhost:8000/admin"

def testar_aprovacao():
    # 1. Ver Lista
    print("📋 A pedir lista de pendentes...")
    resp = requests.get(f"{BASE_URL}/requests")
    pedidos = resp.json()
    print(f"Pendentes: {pedidos}")

    if not pedidos:
        print("Nenhum pedido para aprovar.")
        return

    # 2. Aprovar o primeiro da lista
    id_para_aprovar = pedidos[0]['id']
    print(f"\n✅ A TENTAR APROVAR O PEDIDO ID: {id_para_aprovar}...")
    
    resp_approve = requests.post(f"{BASE_URL}/requests/{id_para_aprovar}/approve")
    
    print(f"Status: {resp_approve.status_code}")
    print(f"Resposta: {resp_approve.json()}")

if __name__ == "__main__":
    testar_aprovacao()