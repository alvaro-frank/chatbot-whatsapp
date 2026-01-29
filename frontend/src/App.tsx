import { useEffect, useState } from 'react';
import './App.css';

interface ServiceRequest {
  id: number;
  customer: string;
  wa_id: string;
  intent: string;
  field_value: string | null;
  response_text: string;
  date: string;
  system_simulation: any;
}

function App() {
  const [requests, setRequests] = useState<ServiceRequest[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchRequests = async () => {
    try {
      const res = await fetch('/admin/requests');
      const data = await res.json();
      setRequests(data);
    } catch (error) {
      console.error("Erro ao buscar pedidos:", error);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  // Nova função para lidar com a edição do texto
  const handleTextChange = (id: number, newText: string) => {
    setRequests(prevRequests =>
      prevRequests.map(req =>
        req.id === id ? { ...req, response_text: newText } : req
      )
    );
  };

  const handleApprove = async (id: number, currentText: string) => {
    // Agora enviamos o texto atual (possivelmente editado)
    if (!confirm("Tem a certeza que quer aprovar e enviar esta mensagem?")) return;
    setLoading(true);

    try {
      const res = await fetch(`/admin/requests/${id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ response_text: currentText }) // <--- Enviamos o texto novo aqui
      });

      if (res.ok) {
        alert("✅ Aprovado com sucesso!");
        fetchRequests();
      } else {
        alert("Erro ao aprovar.");
      }
    } catch (error) {
      console.error(error);
      alert("Erro de conexão.");
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async (id: number, currentText: string) => {
    if (!confirm("Tem a certeza que quer rejeitar? O cliente receberá a mensagem escrita.")) return;
    setLoading(true);
    try {
      const res = await fetch(`/admin/requests/${id}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ response_text: currentText }) // <--- Enviamos o texto aqui
      });

      if (res.ok) {
        fetchRequests();
      } else {
        alert("Erro ao rejeitar.");
      }
    } catch (error) {
      console.error(error);
      alert("Erro de conexão.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '800px', margin: '0 auto' }}>
      <h1>Dashboard Pronegócios</h1>

      {requests.length === 0 ? (
        <p>Nenhum pedido pendente.</p>
      ) : (
        <div style={{ display: 'grid', gap: '20px' }}>
          {requests.map((req) => (
            <div key={req.id} style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '20px',
              backgroundColor: '#fff',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                <h3 style={{ margin: 0 }}>👤 {req.customer}</h3>
                <small style={{ color: '#666' }}>{req.date}</small>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <span style={{
                  backgroundColor: '#eee', padding: '4px 8px', borderRadius: '4px', fontSize: '0.9em', marginRight: '10px'
                }}>
                  {req.intent}
                </span>
              </div>

              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '0.9em', color: '#555' }}>
                  Sugestão IA (Pode editar):
                </label>
                <textarea
                  value={req.response_text}
                  onChange={(e) => handleTextChange(req.id, e.target.value)}
                  style={{
                    width: '100%',
                    minHeight: '80px',
                    padding: '10px',
                    borderRadius: '5px',
                    borderColor: '#ccc',
                    fontFamily: 'inherit',
                    backgroundColor: '#f8f9fa'
                  }}
                />
              </div>

              <div style={{
                marginBottom: '15px',
                border: '1px solid #333',
                borderRadius: '6px',
                overflow: 'hidden'
              }}>
                <div style={{
                  backgroundColor: '#333',
                  color: '#fff',
                  padding: '5px 10px',
                  fontSize: '0.8em',
                  fontFamily: 'monospace',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}>
                </div>
                <div style={{
                  backgroundColor: '#1e1e1e',
                  color: '#00ff00',
                  padding: '10px',
                  fontFamily: 'Consolas, "Courier New", monospace',
                  fontSize: '0.85em',
                  whiteSpace: 'pre-wrap'
                }}>
                  {JSON.stringify(req.system_simulation, null, 2)}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={() => handleApprove(req.id, req.response_text)}
                  disabled={loading}
                  style={{
                    backgroundColor: '#4CAF50', color: 'white', padding: '10px 20px',
                    border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold'
                  }}
                >
                  Aprovar
                </button>
                <button
                  onClick={() => handleReject(req.id, req.response_text)}
                  disabled={loading}
                  style={{
                    backgroundColor: '#f44336', color: 'white', padding: '10px 20px',
                    border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold'
                  }}
                >
                  Rejeitar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;