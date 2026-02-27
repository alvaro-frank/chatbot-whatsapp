import type { ManageRequest } from "../../domain/models/ManageRequest";

export class ManageRequestMapper {
    static toActionResult(raw: any): ManageRequest {
        return {
            request_id: String(raw.request_id),
            customer: raw.customer,
            wa_id: raw.wa_id,
            new_status: raw.new_status,
            message: raw.message,
            processed_at: raw.processed_at
        };
    }
}