import type { ServiceRequest } from '../models/ServiceRequest';

export interface IRequestRepository {
  getPendingRequests(): Promise<ServiceRequest[]>;
  approveRequest(id: number, text: string): Promise<void>;
  rejectRequest(id: number, text: string): Promise<void>;
}