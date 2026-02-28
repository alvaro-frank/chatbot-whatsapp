import type { IRequestRepository } from "../domain/repositories/IRequestRepository";
import type { ManageRequest } from "../domain/models/ManageRequest";

export class RejectRequestUseCase {
    private repository: IRequestRepository;

    constructor(repository: IRequestRepository) {
        this.repository = repository;
    }

    /**
     * Executes the rejection workflow for a specific service request.
     * * Use this when the user's intent is unclear, incorrect, or malicious. 
     * The rejection will prevent any changes to the database and allows the 
     * administrator to send a custom explanation message to the customer.
     *
     * @param {string} id - The unique identifier (UUID) of the request to reject.
     * @param {string} text - The explanation message to be sent to the customer.
     * @returns {Promise<ManageRequest>} An object confirming the rejection status.
     * @throws {Error} If the repository encounter issues during the process.
     */
    async execute(id: string, text: string): Promise<ManageRequest> {
        return await this.repository.rejectRequest(id, text);
    }
}