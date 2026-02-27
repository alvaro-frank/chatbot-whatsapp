import { useState, useEffect, useMemo, useCallback } from 'react';
import type { ServiceRequest } from '../../domain/models/ServiceRequest';
import type { ManageRequest } from '../../domain/models/ManageRequest';
import { useRepository } from '../../presentation/context/RepositoryContext';
import { GetPendingRequestsUseCase } from '../../application/GetPendingRequestsUseCase';
import { ApproveRequestUseCase } from '../../application/ApproveRequestUseCase';
import { RejectRequestUseCase } from '../../application/RejectRequestUseCase';

export function useRequests() {
    const [requests, setRequests] = useState<ServiceRequest[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [processingId, setProcessingId] = useState<string | null>(null);
    const [feedback, setFeedback] = useState<ManageRequest | null>(null);

    const repo = useRepository();

    const getRequestsUC = useMemo(() => new GetPendingRequestsUseCase(repo), [repo]);
    const approveUC = useMemo(() => new ApproveRequestUseCase(repo), [repo]);
    const rejectUC = useMemo(() => new RejectRequestUseCase(repo), [repo]);

    const fetchRequests = useCallback(async () => {
        setIsLoading(true);
        try {
            const data = await getRequestsUC.execute();
            setRequests(data);
        } catch (error) {
            console.error("Erro ao carregar pedidos:", error);
        } finally {
            setIsLoading(false);
        }
    }, [getRequestsUC]);

    useEffect(() => {
        fetchRequests();
        const interval = setInterval(fetchRequests, 30000);
        return () => clearInterval(interval);
    }, [fetchRequests]);

    const handleApprove = async (id: string, text: string) => {
        setProcessingId(id);
        try {
            const result = await approveUC.execute(id, text);
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
            const result = await rejectUC.execute(id, text);
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