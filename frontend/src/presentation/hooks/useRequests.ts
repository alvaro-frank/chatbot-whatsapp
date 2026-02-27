import { useState, useEffect, useCallback } from 'react';
import type { ServiceRequest } from '../../domain/models/ServiceRequest';
import type { ManageRequest } from '../../domain/models/ManageRequest';
import { useUseCases } from '../context/UseCaseContext';

export function useRequests() {
    const [requests, setRequests] = useState<ServiceRequest[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [processingId, setProcessingId] = useState<string | null>(null);
    const [feedback, setFeedback] = useState<ManageRequest | null>(null);

    const { getPendingRequests, approveRequest, rejectRequest } = useUseCases();

    const fetchRequests = useCallback(async () => {
        setIsLoading(true);
        try {
            const data = await getPendingRequests.execute();
            setRequests(data);
        } catch (error) {
            console.error("Erro ao carregar pedidos:", error);
        } finally {
            setIsLoading(false);
        }
    }, [getPendingRequests]);

    useEffect(() => {
        fetchRequests();
        const interval = setInterval(fetchRequests, 30000);
        return () => clearInterval(interval);
    }, [fetchRequests]);

    const handleApprove = async (id: string, text: string) => {
        setProcessingId(id);
        try {
            const result = await approveRequest.execute(id, text);
            setRequests(prev => prev.filter(r => r.id !== id));
            setFeedback(result);
            setTimeout(() => setFeedback(null), 5000);
        } catch (error) {
            console.error("Erro na aprovação:", error);
        } finally {
            setProcessingId(null);
        }
    };

    const handleReject = async (id: string, text: string) => {
        setProcessingId(id);
        try {
            const result = await rejectRequest.execute(id, text);
            setRequests(prev => prev.filter(r => r.id !== id));
            setFeedback(result);
            setTimeout(() => setFeedback(null), 5000);
        } catch (error) {
            console.error("Erro na rejeição:", error);
        } finally {
            setProcessingId(null);
        }
    };

    const handleUpdateLocalText = (id: string, newText: string) => {
        setRequests(prev => prev.map(req =>
            req.id === id ? { ...req, generated_response: newText } : req
        ));
    };

    return {
        requests,
        isLoading,
        processingId,
        feedback,
        setFeedback,
        handleApprove,
        handleReject,
        handleUpdateLocalText
    };
}