import { useState, useEffect, useCallback } from 'react';
import type { ServiceRequest } from '../domain/models/ServiceRequest';
import { useRepository } from '../infrastructure/context/RepositoryContext';

export function useRequests() {
    const [requests, setRequests] = useState<ServiceRequest[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [processingId, setProcessingId] = useState<number | null>(null);

    const repo = useRepository();

    const fetchRequests = useCallback(async () => {
        setIsLoading(true);
        try {
            const data = await repo.getPendingRequests();
            setRequests(data);
        } catch (error) {
            console.error("Erro ao carregar:", error);
        } finally {
            setIsLoading(false);
        }
    }, [repo]);

    useEffect(() => {
        fetchRequests();
        const interval = setInterval(fetchRequests, 30000);
        return () => clearInterval(interval);
    }, [fetchRequests]);

    const handleApprove = async (id: number, text: string) => {
        if (!confirm("Confirmar aprovação?")) return;
        setProcessingId(id);
        try {
            await repo.approveRequest(id, text);
            setRequests(prev => prev.filter(r => r.id !== id));
        } catch (error) {
            alert("Erro ao aprovar");
        } finally {
            setProcessingId(null);
        }
    };

    const handleReject = async (id: number, text: string) => {
        if (!confirm("Tem a certeza que deseja rejeitar? O cliente será notificado.")) return;
        setProcessingId(id);
        try {
            await repo.rejectRequest(id, text);
            setRequests(prev => prev.filter(r => r.id !== id));
        } catch (error) {
            alert("Erro ao rejeitar.");
        } finally {
            setProcessingId(null);
        }
    };

    const handleUpdateLocalText = (id: number, newText: string) => {
        setRequests(prev => prev.map(req =>
            req.id === id ? { ...req, response_text: newText } : req
        ));
    };

    return {
        requests,
        isLoading,
        processingId,
        fetchRequests,
        handleApprove,
        handleReject,
        handleUpdateLocalText,
        reload: fetchRequests
    };
}