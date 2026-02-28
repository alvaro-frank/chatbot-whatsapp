/**
 * Represents the final outcome of an administrative action (Approval or Rejection).
 * * This domain entity encapsulates the data returned by the system after a request 
 * has been processed. It serves as the single source of truth for the presentation 
 * layer to display success/error banners and update the local state.
 * * Attributes:
 * @property {string} requestId - The unique UUID of the processed request.
 * @property {string} customer - The full name of the customer for personalized feedback.
 * @property {string} waId - The WhatsApp identifier used for the notification.
 * @property {string} newStatus - The finalized state ('APPROVED' or 'REJECTED').
 * @property {string} message - A descriptive summary of the operation's result.
 * @property {string} processedAt - ISO-8601 formatted timestamp of the execution.
 */
export interface ManageRequest {
  request_id: string;
  customer: string;
  wa_id: string;
  new_status: 'APPROVED' | 'REJECTED';
  message: string;
  processed_at: string;
}