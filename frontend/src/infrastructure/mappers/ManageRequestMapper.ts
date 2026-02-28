import type { ManageRequest } from "../../domain/models/ManageRequest";

export class ManageRequestMapper {
    /**
     * Transforms a raw JSON response from an approval or rejection action into a ManageRequest entity.
     * * This method specifically handles the result of administrative commands, ensuring 
     * that identifiers are correctly cast to strings and that all required feedback 
     * fields (customer name, status, etc.) are present and correctly typed for the UI.
     *
     * Args:
     * @param {any} raw - The unvalidated JSON payload received from the Backend API.
     *
     * Returns:
     * @returns {ManageRequest} A structured Domain Entity representing the action's outcome.
     *
     * Raises:
     * @throws {TypeError} If the raw data is null or missing critical mapping fields.
     */
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