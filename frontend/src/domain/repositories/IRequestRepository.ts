import type { ServiceRequest } from '../models/ServiceRequest';
import type { ManageRequest } from '../models/ManageRequest';

export interface IRequestRepository {
  /**
     * Fetches all service requests currently awaiting administrative review.
     * * Retrieves a raw collection from the data source and expects the adapter 
     * to map them into Domain Entities.
     *
     * @returns {Promise<ServiceRequest[]>} A list of entities ready for processing.
     * @throws {Error} If the connection to the data source is lost or the data is malformed.
     */
  getPendingRequests(): Promise<ServiceRequest[]>;

  /**
     * Submits a formal approval for a specific request.
     * * This operation transitions the request state and triggers the delivery 
     * of the final message to the customer.
     *
     * @param {string} id - The unique UUID of the request.
     * @param {string} text - The final message content to be sent via WhatsApp.
     * @returns {Promise<ManageRequest>} The result of the operation including the new status.
     */
  approveRequest(id: string, text: string): Promise<ManageRequest>;

  /**
     * Submits a formal rejection for a specific request.
     * * Effectively cancels the request and notifies the customer of the decision.
     *
     * @param {string} id - The unique UUID of the request.
     * @param {string} text - The explanation or reason for the rejection.
     * @returns {Promise<ManageRequest>} The result of the operation.
     */
  rejectRequest(id: string, text: string): Promise<ManageRequest>;
}