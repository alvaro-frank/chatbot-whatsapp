import type { ServiceRequest } from '../models/ServiceRequest';

export interface IRequestRepository {
  getPendingRequests(): Promise<ServiceRequest[]>;
  approveRequest(id: string, text: string): Promise<void>;
  rejectRequest(id: string, text: string): Promise<void>;
}