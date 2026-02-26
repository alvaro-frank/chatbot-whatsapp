// Interface representing a service request in the application
export interface ServiceRequest {
  id: string;
  customer: string;
  wa_id: string;
  intent: string;
  field_value: string | null;
  response_text: string;
  date: string;
  system_simulation: any;
  user_input: string;
}