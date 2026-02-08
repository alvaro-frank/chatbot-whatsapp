# ==============================================================================
# FILE: app/commands/command_factory.py
# DESCRIPTION: Maps intent strings to specific Command classes.
# ==============================================================================

from app.commands.simulation_commands import AlterarNifCommand, AlterarMoradaCommand, DefaultSimulationCommand

class CommandFactory:
    _commands = {
        "alterar_nif": AlterarNifCommand(),
        "alterar_morada": AlterarMoradaCommand(),
    }

    @staticmethod
    def get_command(intent: str):
        return CommandFactory._commands.get(intent, DefaultSimulationCommand())