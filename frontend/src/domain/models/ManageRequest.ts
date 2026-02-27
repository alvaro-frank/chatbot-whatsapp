// Interface representing a managed request in the application
export interface ManageRequest {
  request_id: string;
  customer: string;
  wa_id: string;
  new_status: 'APPROVED' | 'REJECTED';
  message: string;
  processed_at: string;
}