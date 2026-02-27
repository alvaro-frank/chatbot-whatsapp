import './App.css';
import { useRequests } from './presentation/hooks/useRequests';
import { RequestCard } from './presentation/components/RequestCard';
import { FeedbackBanner } from './presentation/components/FeedbackBanner';

function App() {
  const {
    requests,
    isLoading,
    processingId,
    handleApprove,
    handleReject,
    handleUpdateLocalText,
    feedback,
    setFeedback
  } = useRequests();

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      {feedback && (
        <FeedbackBanner 
          feedback={feedback} 
          onClose={() => setFeedback(null)} 
        />
      )}

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
    </div> 
  );
}

export default App;