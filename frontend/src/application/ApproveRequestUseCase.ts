import type { IRequestRepository } from "../domain/repositories/IRequestRepository";
import type { ManageRequest } from "../domain/models/ManageRequest";

export class ApproveRequestUseCase {
    private repository: IRequestRepository;

    constructor(repository: IRequestRepository) {
        this.repository = repository;
    }

    async execute(id: string, text: string): Promise<ManageRequest> {
        if (!id) throw new Error("ID do pedido é obrigatório.");
        return await this.repository.approveRequest(id, text);
    }
}