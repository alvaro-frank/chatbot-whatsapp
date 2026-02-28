import type { IRequestRepository } from '../../domain/repositories/IRequestRepository';
import type { ServiceRequest } from '../../domain/models/ServiceRequest';
import type { ManageRequest } from '../../domain/models/ManageRequest';
import { RequestMapper } from '../mappers/ServiceRequestMapper';
import { ManageRequestMapper } from '../mappers/ManageRequestMapper';

export class HttpRequestRepository implements IRequestRepository {
  /**
     * Retrieves the collection of pending service requests from the remote server.
     * * Fetches data from the '/admin/requests/' endpoint and utilizes the 
     * RequestMapper to transform the raw JSON response into Domain Entities. 
     * This ensures that any change in the backend's JSON structure only 
     * requires a modification in the Mapper, not the Repository or UI.
     *
     * @returns {Promise<ServiceRequest[]>} A collection of validated ServiceRequest objects.
     * @throws {Error} "Pending Request Loading Error" if the server responds with a non-OK status.
     */
  async getPendingRequests(): Promise<ServiceRequest[]> {
    const res = await fetch('/admin/requests/'); 

    if (!res.ok) throw new Error("Pending Request Loading Error");

    const data = await res.json();
    return data.map(RequestMapper.toDomain);
  }

  /**
     * Executes an approval action for a specific request via a POST request.
     * * Sends the administrator's final response text to the server to finalize 
     * the request lifecycle. The response is then mapped back to a ManageRequest 
     * object to provide feedback to the UI.
     *
     * @param {string} id - The unique UUID of the request to approve.
     * @param {string} text - The manually reviewed or edited AI response text.
     * @returns {Promise<ManageRequest>} The result of the approval including the new status.
     * @throws {Error} "Request Approval Error" if the API call fails or validation fails on the server.
     */
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

  /**
     * Executes a rejection action for a specific request via a POST request.
     * * Notifies the backend that the request should be marked as REJECTED. 
     * Similar to the approval, it sends a final explanation text to be 
     * dispatched to the customer.
     *
     * @param {string} id - The unique UUID of the request to reject.
     * @param {string} text - The reason or message explaining the rejection.
     * @returns {Promise<ManageRequest>} The result of the rejection operation.
     * @throws {Error} "Request Rejection Error" if the network operation fails.
     */
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