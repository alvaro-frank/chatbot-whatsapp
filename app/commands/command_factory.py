# ==============================================================================
# FILE: app/commands/command_factory.py
# DESCRIPTION: Maps intent strings to specific Command classes.
# ==============================================================================

from app.commands.simulation_commands import AlterarNifCommand, DefaultSimulationCommand

class CommandFactory:
    _commands = {
        "alterar_nif": AlterarNifCommand()
    }

    @staticmethod
    def get_command(intent: str):
        return CommandFactory._commands.get(intent, DefaultSimulationCommand())