import type { ServiceRequest } from '../domain/models/ServiceRequest';

interface RequestCardProps {
    request: ServiceRequest;
    isProcessing: boolean;
    onApprove: (id: number, text: string) => void;
    onReject: (id: number, text: string) => void;
    onTextChange: (id: number, text: string) => void;
}

export function RequestCard({ request, isProcessing, onApprove, onReject, onTextChange }: RequestCardProps) {
    return (
        <div className="request-card">
            <div className="card-header">
                <div>
                    <h3 className="customer-name">{request.customer}</h3>
                    <span className="wa-id">+{request.wa_id}</span>
                </div>
                <span className="message-date">{request.date}</span>
            </div>

            <div className="meta-data">
                <span className="badge badge-intent">
                    Operação: {request.intent.replace('_', ' ')}
                </span>
            </div>

            <div style={{
                backgroundColor: '#f8fafc',
                borderRadius: '12px',
                padding: '15px',
                margin: '15px 0',
                border: '1px solid #e2e8f0'
            }}>
                {/* Mensagem do Cliente */}
                <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                    <div style={{
                        width: '35px', height: '35px', minWidth: '35px', borderRadius: '50%',
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
                        <strong>{request.customer}:</strong><br />
                        {request.user_input}
                    </div>
                </div>

                {/* Sugestão do Bot (Editável) */}
                <div style={{ display: 'flex', gap: '10px', flexDirection: 'row-reverse' }}>
                    <div style={{
                        width: '35px', height: '35px', minWidth: '35px', borderRadius: '50%',
                        backgroundColor: '#3b82f6', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>🤖</div>
                    <div style={{ width: '100%', maxWidth: '80%' }}>
                        <div style={{ marginBottom: '5px', fontSize: '0.8rem', textAlign: 'right', color: '#64748b' }}>
                            Sugestão de Resposta:
                        </div>
                        <textarea
                            className="response-input"
                            value={request.response_text}
                            onChange={(e) => onTextChange(request.id, e.target.value)}
                            style={{
                                borderRadius: '12px 0 12px 12px',
                                border: '2px solid #3b82f6',
                                width: '100%',
                                minHeight: '80px'
                            }}
                        />
                    </div>
                </div>
            </div>

            <div className="simulation-container">
                <div className="terminal-body">
                    {JSON.stringify(request.system_simulation, null, 2)}
                </div>
            </div>

            <div className="actions">
                <button
                    className="btn-approve"
                    onClick={() => onApprove(request.id, request.response_text)}
                    disabled={isProcessing}
                >
                    {isProcessing ? 'A processar...' : '✓ Aprovar'}
                </button>
                <button
                    className="btn-reject"
                    onClick={() => onReject(request.id, request.response_text)}
                    disabled={isProcessing}
                >
                    ✕ Rejeitar
                </button>
            </div>
        </div>
    );
}