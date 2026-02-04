import './App.css';
import { useRequests } from './hooks/useRequests';
import { RequestCard } from './components/RequestCard';

function App() {
  const { 
    requests, 
    isLoading, 
    processingId, 
    handleApprove, 
    handleReject,
    handleUpdateLocalText 
  } = useRequests();

  return (
    <div className="app-container">
      <header className="header">
        <div className="brand">Pronegócios Dashboard</div>
      </header>

      {isLoading && requests.length === 0 && (
        <div className="status-message">Carregando pedidos...</div>
      )}

      {!isLoading && requests.length === 0 && (
        <div className="empty-state">
          <h2>Não existem pedidos pendentes.</h2>
        </div>
      )}

      <div className="requests-list">
        {requests.map((req) => (
          <RequestCard
            key={req.id}
            request={req}
            isProcessing={processingId === req.id}
            onApprove={handleApprove}
            onReject={handleReject}
            onTextChange={handleUpdateLocalText}
          />
        ))}
      </div>
    </div>
  );
}

export default App;