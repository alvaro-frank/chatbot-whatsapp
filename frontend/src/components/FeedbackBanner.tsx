import React, { useEffect, useState } from 'react';
import { CheckCircle2, AlertCircle, X, Clock } from 'lucide-react';
import type { ManageRequest } from '../domain/models/ManageRequest';

interface FeedbackBannerProps {
  feedback: ManageRequest;
  onClose: () => void;
  duration?: number;
}

export const FeedbackBanner: React.FC<FeedbackBannerProps> = ({ 
  feedback, 
  onClose, 
  duration = 5000 
}) => {
  const [progress, setProgress] = useState(100);
  const isApproved = feedback.new_status === 'APPROVED';

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prev) => Math.max(0, prev - (100 / (duration / 100))));
    }, 100);

    return () => clearInterval(timer);
  }, [duration]);

  return (
    <div className="fixed top-6 right-6 z-[100] w-[400px] pointer-events-auto group">
      <div className={`relative overflow-hidden rounded-2xl border backdrop-blur-md shadow-2xl transition-all duration-500 hover:scale-[1.02]
        ${isApproved 
          ? 'bg-white/90 border-green-200/50 shadow-green-900/10' 
          : 'bg-white/90 border-red-200/50 shadow-red-900/10'}`}>
        
        <div className="p-5">
          <div className="flex items-start gap-4">
            <div className={`flex-shrink-0 flex items-center justify-center w-12 h-12 rounded-xl transition-transform duration-500 group-hover:rotate-12
              ${isApproved ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
              {isApproved ? <CheckCircle2 size={24} /> : <AlertCircle size={24} />}
            </div>

            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-bold text-gray-900 mb-1 leading-tight">
                {feedback.message}
              </h3>
              
              <div className="flex flex-col gap-1.5">
                <div className="flex items-center text-[11px] font-medium text-gray-500 uppercase tracking-wider">
                  <span className="w-1.5 h-1.5 rounded-full bg-gray-300 mr-2" />
                  Cliente: <span className="text-gray-900 ml-1">{feedback.customer}</span>
                </div>
                
                <div className="flex items-center text-[11px] font-medium text-gray-400">
                  <Clock size={12} className="mr-1.5" />
                  {feedback.processed_at}
                </div>
              </div>
            </div>

            <button
              onClick={onClose}
              className="flex-shrink-0 p-1 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-900 transition-all"
            >
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="absolute bottom-0 left-0 h-1 w-full bg-gray-100/50">
          <div 
            className={`h-full transition-all duration-100 ease-linear
              ${isApproved ? 'bg-green-500' : 'bg-red-500'}`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
};