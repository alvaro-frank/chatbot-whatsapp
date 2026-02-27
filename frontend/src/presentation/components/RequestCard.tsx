import { useState } from 'react';
import type { ServiceRequest } from '../../domain/models/ServiceRequest';

interface RequestCardProps {
    request: ServiceRequest;
    isProcessing: boolean;
    onApprove: (id: string, text: string) => void;
    onReject: (id: string, text: string) => void;
    onTextChange: (id: string, text: string) => void;
}

export function RequestCard({ request, isProcessing, onApprove, onReject, onTextChange }: RequestCardProps) {
    const [isFlipped, setIsFlipped] = useState(false);

    const handleFlip = () => setIsFlipped(!isFlipped);

    return (
        <div className={`flip-card ${isFlipped ? 'is-flipped' : ''}`} onClick={handleFlip}>
            <div className="flip-card-inner">
                
                <div className="flip-card-front request-card" onClick={(e) => e.stopPropagation()}>
                    <div className="card-header" onClick={handleFlip} style={{ cursor: 'help' }}>
                        <div>
                            <h3 className="customer-name">{request.customer}</h3>
                            <span className="wa-id">+{request.wa_id}</span>
                        </div>
                        <span className="message-date">{request.date}</span>
                    </div>

                    <div className="meta-data">
                        <span className="badge badge-intent">
                            Operação: {request.intent.replace(/_/g, ' ')}
                        </span>
                    </div>

                    <div className="chat-container">
                        <div className="message-row">
                            <div className="avatar avatar-user">👤</div>
                            <div className="bubble">
                                <strong>{request.customer}:</strong><br />
                                {request.user_input}
                            </div>
                        </div>

                        <div className="message-row bot">
                            <div className="avatar avatar-bot">🤖</div>
                            <div className="bot-input-wrapper">
                                <div className="input-label">Sugestão de Resposta:</div>
                                <textarea
                                    className="response-textarea"
                                    value={request.response_text}
                                    onClick={(e) => e.stopPropagation()}
                                    onChange={(e) => onTextChange(request.id, e.target.value)}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="actions" onClick={(e) => e.stopPropagation()}>
                        <button 
                            className="btn-approve" 
                            onClick={() => onApprove(request.id, request.response_text)} 
                            disabled={isProcessing}
                        >
                            {isProcessing ? '...' : '✓ Aprovar'}
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

                <div className="flip-card-back">
                    <div className="terminal-header">
                        <span>DEBUG_VIEW.exe</span>
                        <span style={{ float: 'right' }}>Clique para voltar</span>
                    </div>
                    <pre className="terminal-body">
                        {JSON.stringify(request.system_simulation, null, 2)}
                    </pre>
                </div>

            </div>
        </div>
    );
}