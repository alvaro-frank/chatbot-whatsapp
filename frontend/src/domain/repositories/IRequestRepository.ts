import type { ServiceRequest } from '../models/ServiceRequest';
import type { ManageRequest } from '../models/ManageRequest';

export interface IRequestRepository {
  getPendingRequests(): Promise<ServiceRequest[]>;
  approveRequest(id: string, text: string): Promise<ManageRequest>;
  rejectRequest(id: string, text: string): Promise<ManageRequest>;
}