// src/application/use_cases/GetPendingRequestsUseCase.ts
import type { IRequestRepository } from "../domain/repositories/IRequestRepository";
import type { ServiceRequest } from "../domain/models/ServiceRequest";

export class GetPendingRequestsUseCase {
    private repository: IRequestRepository;

    constructor(repository: IRequestRepository) {
        this.repository = repository;
    }

    /**
     * Orchestrates the retrieval of all service requests awaiting administrative review.
     * * This use case acts as the primary data fetcher for the dashboard, ensuring that
     * raw data from the infrastructure layer is properly surfaced to the presentation layer
     * as Domain Entities.
     *
     * @returns {Promise<ServiceRequest[]>} A collection of ServiceRequest entities ready for UI display.
     * @throws {Error} If the repository fails to connect or returns an invalid response.
     */
    async execute(): Promise<ServiceRequest[]> {
        return await this.repository.getPendingRequests();
    }
}