from app.application.commands.base_command import BaseSimulationCommand

class AlterarNifCommand(BaseSimulationCommand):
    """
    Simulation command for Tax ID (NIF) updates.
    
    Prepares the metadata required to update a customer's fiscal identification 
    within the CRM system.
    """
    def execute(self, request_model) -> dict:
        """
        Generates a simulation payload for a NIF update operation.

        Returns:
            dict: Mapping of the target table, the new NIF value, and the lookup criteria.
        """
        return {
            "action": request_model.intent,
            "target_table": "TABELA_CLIENTES_CRM",
            "parameters": {"value": request_model.field_value},
            "where": {"client_id": "CRM_ID_PLACEHOLDER"}
        }
        
class AlterarMoradaCommand(BaseSimulationCommand):
    """
    Simulation command for Address (Morada) updates.
    
    Prepares the metadata required to update a customer's physical or 
    billing address in the CRM system.
    """
    def execute(self, request_model) -> dict:
        """
        Generates a simulation payload for an address update operation.

        Returns:
            dict: Mapping of the target table, the new address string, and the lookup criteria.
        """
        return {
            "action": request_model.intent,
            "target_table": "TABELA_CLIENTES_CRM",
            "parameters": {"value": request_model.field_value},
            "where": {"client_id": "CRM_ID_PLACEHOLDER"}
        }

class DefaultSimulationCommand(BaseSimulationCommand):
    """
    Simulation command for Address (Morada) updates.
    
    Prepares the metadata required to update a customer's physical or 
    billing address in the CRM system.
    """
    def execute(self, request_model) -> dict:
        """
        Returns an empty result indicating no automated simulation is available.
        """
        return {}