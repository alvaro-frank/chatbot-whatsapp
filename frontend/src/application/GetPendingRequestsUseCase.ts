// src/application/use_cases/GetPendingRequestsUseCase.ts
import type { IRequestRepository } from "../domain/repositories/IRequestRepository";
import type { ServiceRequest } from "../domain/models/ServiceRequest";

export class GetPendingRequestsUseCase {
    private repository: IRequestRepository;

    constructor(repository: IRequestRepository) {
        this.repository = repository;
    }

    async execute(): Promise<ServiceRequest[]> {
        return await this.repository.getPendingRequests();
    }
}