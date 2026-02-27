import type { IRequestRepository } from '../../domain/repositories/IRequestRepository';
import type { ServiceRequest } from '../../domain/models/ServiceRequest';
import type { ManageRequest } from '../../domain/models/ManageRequest';
import { RequestMapper } from '../mappers/ServiceRequestMapper';
import { ManageRequestMapper } from '../mappers/ManageRequestMapper';

export class HttpRequestRepository implements IRequestRepository {
  async getPendingRequests(): Promise<ServiceRequest[]> {
    const res = await fetch('/admin/requests/'); 

    if (!res.ok) throw new Error("Pending Request Loading Error");

    const data = await res.json();
    return data.map(RequestMapper.toDomain);
  }

  async approveRequest(id: string, text: string): Promise<ManageRequest> {
    const res = await fetch(`/admin/requests/${id}/approve`, { //
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ response_text: text })
    });

    if (!res.ok) throw new Error("Request Approval Error");
    
    const data = await res.json();
    return ManageRequestMapper.toActionResult(data);
  }

  async rejectRequest(id: string, text: string): Promise<ManageRequest> {
    const res = await fetch(`/admin/requests/${id}/reject`, { //
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ response_text: text })
    });

    if (!res.ok) throw new Error("Request Rejection Error");
    
    const data = await res.json();
    return ManageRequestMapper.toActionResult(data);
  }
}