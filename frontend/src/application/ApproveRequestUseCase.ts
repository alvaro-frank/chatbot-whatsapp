import type { IRequestRepository } from "../domain/repositories/IRequestRepository";
import type { ManageRequest } from "../domain/models/ManageRequest";

export class ApproveRequestUseCase {
    private repository: IRequestRepository;

    constructor(repository: IRequestRepository) {
        this.repository = repository;
    }

    /**
     * Executes the approval workflow for a specific service request.
     * * This process confirms the AI-generated changes, triggers the actual update 
     * in the backend systems, and prepares the final confirmation message 
     * to be sent back to the customer via WhatsApp.
     *
     * @param {string} id - The unique identifier (UUID) of the request to approve.
     * @param {string} text - The final version of the response text to be sent to the user.
     * @returns {Promise<ManageRequest>} An object containing the operation result and metadata.
     * @throws {Error} If the ID is missing or if the repository operation fails.
     */
    async execute(id: string, text: string): Promise<ManageRequest> {
        if (!id) throw new Error("ID do pedido é obrigatório.");
        return await this.repository.approveRequest(id, text);
    }
}