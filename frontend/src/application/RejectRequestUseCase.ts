import type { IRequestRepository } from "../domain/repositories/IRequestRepository";
import type { ManageRequest } from "../domain/models/ManageRequest";

export class RejectRequestUseCase {
    private repository: IRequestRepository;

    constructor(repository: IRequestRepository) {
        this.repository = repository;
    }

    async execute(id: string, text: string): Promise<ManageRequest> {
        return await this.repository.rejectRequest(id, text);
    }
}