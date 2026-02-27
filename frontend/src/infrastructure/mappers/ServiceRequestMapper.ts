import type { ServiceRequest } from "../../domain/models/ServiceRequest";

export class RequestMapper {
    static toDomain(raw: any): ServiceRequest {
        return {
            id: String(raw.id),
            customer: raw.customer || raw.customer_name,
            wa_id: raw.wa_id,
            intent: raw.intent,
            user_input: raw.user_input,
            field_value: raw.field_value,
            response_text: raw.response_text || raw.generated_response,
            date: raw.date || raw.created_at,
            system_simulation: raw.system_simulation || raw.simulation_data || null
        };
    }
}