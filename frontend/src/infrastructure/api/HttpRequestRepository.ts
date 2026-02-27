import type { IRequestRepository } from '../../domain/repositories/IRequestRepository';
import type { ServiceRequest } from '../../domain/models/ServiceRequest';
import type { ManageRequest } from '../../domain/models/ManageRequest';

export class HttpRequestRepository implements IRequestRepository {
  async getPendingRequests(): Promise<ServiceRequest[]> {
    const res = await fetch('/admin/requests/'); //
    if (!res.ok) throw new Error("Falha ao carregar pedidos.");
    return res.json();
  }

  async approveRequest(id: string, text: string): Promise<ManageRequest> {
    const res = await fetch(`/admin/requests/${id}/approve`, { //
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ response_text: text })
    });
    if (!res.ok) throw new Error("Erro na aprovação.");
    return res.json();
  }

  async rejectRequest(id: string, text: string): Promise<ManageRequest> {
    const res = await fetch(`/admin/requests/${id}/reject`, { //
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ response_text: text })
    });
    if (!res.ok) throw new Error("Erro na rejeição.");
    return res.json();
  }
}