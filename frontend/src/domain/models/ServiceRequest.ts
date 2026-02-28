/**
 * Represents a core business entity for a service request received via WhatsApp.
 * * This entity encapsulates the state, metadata, and simulated logic for a user's request. 
 * It acts as the "Source of Truth" for the dashboard, containing both the raw input 
 * and the system's proposed resolution (AI analysis and simulation). By using a class 
 * instead of a simple interface, we centralize UI logic (like date formatting or 
 * intent mapping) within the domain itself, following the Rich Domain Model pattern.
 * * Attributes:
 * @property {string} id - The unique UUID identifying the request in the database.
 * @property {string} customer - The display name or profile name of the sender.
 * @property {string} wa_id - The unique WhatsApp identifier (phone number) of the user.
 * @property {string} intent - The business intent classified by the AI (e.g., 'alterar_nif').
 * @property {string | null} field_value - The specific data entity extracted (e.g., the new NIF number).
 * @property {string} response_text - The AI-generated response draft prepared for the customer.
 * @property {string} date - ISO-8601 formatted timestamp of when the request was received.
 * @property {any} system_simulation - Metadata containing the predicted side-effects of the request.
 * @property {string} user_input - The raw, original text message sent by the customer.
 * @property {string} status - The current lifecycle state ('PENDING', 'APPROVED', 'REJECTED').
 */
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