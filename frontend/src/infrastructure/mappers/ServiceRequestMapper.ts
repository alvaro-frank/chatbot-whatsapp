import type { ServiceRequest } from "../../domain/models/ServiceRequest";

export class RequestMapper {
    /**
     * Transforms a raw JSON object from the backend API into a structured ServiceRequest Domain Entity.
     * * This method handles the normalization of varying technical field names (e.g., fallback 
     * mechanisms for 'customer_name' vs 'customer') and ensures that all identifiers are 
     * cast to strings (UUIDs) to maintain type consistency across the frontend. It also 
     * packages the complex simulation metadata and AI-generated responses into a 
     * standardized contract for the dashboard.
     *
     * Args:
     * @param {any} raw - The unvalidated JSON payload received from the administrative API endpoints.
     *
     * Returns:
     * @returns {ServiceRequest} A normalized ServiceRequest object containing enriched data for the UI.
     *
     * Raises:
     * @throws {Error} If critical mapping logic fails or if the raw data is fundamentally malformed.
     */
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