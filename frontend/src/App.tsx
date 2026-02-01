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
  user_input: string;
}

function App() {
  const [requests, setRequests] = useState<ServiceRequest[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [processingId, setProcessingId] = useState<number | null>(null);
  const fetchRequests = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/admin/requests/');
      if (!res.ok) throw new Error("Falha na rede");
      const data = await res.json();
      setRequests(data);
    } catch (error) {
      console.error("Erro ao carregar:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
    const interval = setInterval(fetchRequests, 30000);
    return () => clearInterval(interval);
  }, []);
  const handleTextChange = (id: number, newText: string) => {
    setRequests(prev => prev.map(req =>
      req.id === id ? { ...req, response_text: newText } : req
    ));
  };
  const handleApprove = async (id: number, finalResponse: string) => {
    if (!confirm("Confirmar aprovação e envio da mensagem?")) return;

    setProcessingId(id);
    try {
      const res = await fetch(`/admin/requests/${id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ response_text: finalResponse })
      });

      if (res.ok) {
        setRequests(prev => prev.filter(r => r.id !== id));
        alert("✅ Processado com sucesso!");
      } else {
        alert("❌ Erro ao processar pedido.");
      }
    } catch (error) {
      alert("Erro de conexão.");
    } finally {
      setProcessingId(null);
      fetchRequests();
    }
  };
  const handleReject = async (id: number, explanation: string) => {
    if (!confirm("Tem a certeza que deseja rejeitar? O cliente será notificado.")) return;

    setProcessingId(id);
    try {
      const res = await fetch(`/admin/requests/${id}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ response_text: explanation })
      });

      if (res.ok) {
        setRequests(prev => prev.filter(r => r.id !== id));
      } else {
        alert("Erro ao rejeitar.");
      }
    } catch (error) {
      alert("Erro de conexão.");
    } finally {
      setProcessingId(null);
      fetchRequests();
    }
  };

  return (
    <div className="app-container">
      {/* HEADER */}
      <header className="header">
        <div className="brand">Pronegócios Dashboard</div>
      </header>

      {/* LOADING STATE */}
      {isLoading && requests.length === 0 && (
        <div style={{ textAlign: 'center', padding: '20px' }}>Carregando pedidos...</div>
      )}

      {/* EMPTY STATE */}
      {!isLoading && requests.length === 0 && (
        <div className="empty-state">
          <h2>Não existem pedidos pendentes neste momento.</h2>
        </div>
      )}

      {/* REQUESTS LIST */}
      <div className="requests-list">
        {requests.map((req) => (
          <div key={req.id} className="request-card">

            <div className="card-header">
              <div>
                <h3 className="customer-name">{req.customer}</h3>
                <span className="wa-id">+{req.wa_id}</span>
              </div>
              <span className="message-date">{req.date}</span>
            </div>

            <div className="meta-data">
              <span className="badge badge-intent">
                Operação: {req.intent.replace('_', ' ')}
              </span>
            </div>

            <div style={{
              backgroundColor: '#f8fafc',
              borderRadius: '12px',
              padding: '15px',
              margin: '15px 0',
              border: '1px solid #e2e8f0'
            }}>

              <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                <div style={{
                  width: '35px', height: '35px', borderRadius: '50%',
                  backgroundColor: '#cbd5e1', display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>👤</div>
                <div style={{
                  backgroundColor: '#fff',
                  padding: '10px 15px',
                  borderRadius: '0 12px 12px 12px',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                  maxWidth: '80%',
                  fontSize: '0.9rem',
                  color: '#334155'
                }}>
                  <strong>{req.customer}:</strong><br />
                  {req.user_input}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '10px', flexDirection: 'row-reverse' }}>
                <div style={{
                  width: '35px', height: '35px', borderRadius: '50%',
                  backgroundColor: '#3b82f6', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>🤖</div>
                <div style={{ width: '100%', maxWidth: '80%' }}>
                  <strong>
                    <div style={{ marginBottom: '5px', fontSize: '0.8rem', textAlign: 'right', color: '#64748b' }}>
                      Sugestão de Resposta:
                    </div>
                  </strong>
                  <textarea
                    className="response-input"
                    value={req.response_text}
                    onChange={(e) => handleTextChange(req.id, e.target.value)}
                    style={{
                      borderRadius: '12px 0 12px 12px',
                      border: '2px solid #3b82f6'
                    }}
                  />
                </div>
              </div>
            </div>

            <div className="simulation-container">
              <div className="terminal-header">
                <span className="terminal-dot"></span>
                <span className="terminal-dot"></span>
                <span className="terminal-dot"></span>
                <span>SYSTEM_PREVIEW.exe</span>
              </div>
              <div className="terminal-body">
                {JSON.stringify(req.system_simulation, null, 2)}
              </div>
            </div>

            <div className="actions">
              <button
                className="btn-approve"
                onClick={() => handleApprove(req.id, req.response_text)}
                disabled={processingId === req.id}
              >
                {processingId === req.id ? 'A processar...' : '✓ Aprovar'}
              </button>

              <button
                className="btn-reject"
                onClick={() => handleReject(req.id, req.response_text)}
                disabled={processingId === req.id}
              >
                ✕ Rejeitar
              </button>
            </div>

          </div>
        ))}
      </div>
    </div>
  );
}

export default App;