# ==============================================================================
# FILE: app/commands/simulation_commands.py
# DESCRIPTION: Concrete implementations of simulation logic per intent.
# ==============================================================================

from app.commands.base_command import BaseSimulationCommand

class AlterarNifCommand(BaseSimulationCommand):
    def execute(self, request_model) -> dict:
        return {
            "action": request_model.intent,
            "target_table": "TABELA_CLIENTES_CRM",
            "parameters": {"value": request_model.field_value},
            "where": {"client_id": "CRM_ID_PLACEHOLDER"}
        }

class DefaultSimulationCommand(BaseSimulationCommand):
    def execute(self, request_model) -> dict:
        return {}