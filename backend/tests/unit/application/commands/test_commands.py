import pytest
from unittest.mock import MagicMock

from app.application.commands.command_factory import CommandFactory
from app.application.commands.simulation_commands import (
    AlterarNifCommand,
    AlterarMoradaCommand,
    DefaultSimulationCommand
)

"""
Command Factory
"""
def test_command_factory_is_actionable_intent_true():
    assert CommandFactory.is_actionable_intent("alterar_nif") is True
    assert CommandFactory.is_actionable_intent("alterar_morada") is True

def test_command_factory_is_actionable_intent_false():
    assert CommandFactory.is_actionable_intent("saudacao") is False
    assert CommandFactory.is_actionable_intent("unknown_intent") is False

def test_command_factory_get_command_returns_specific_commands():
    cmd_nif = CommandFactory.get_command("alterar_nif")
    assert isinstance(cmd_nif, AlterarNifCommand)
    
    cmd_morada = CommandFactory.get_command("alterar_morada")
    assert isinstance(cmd_morada, AlterarMoradaCommand)

def test_command_factory_get_command_returns_default_for_unknown():
    cmd_default = CommandFactory.get_command("falar_com_humano")
    assert isinstance(cmd_default, DefaultSimulationCommand)

"""
Simulation Commands
"""

@pytest.fixture
def mock_request_model():
    mock = MagicMock()
    mock.intent = "simulated_intent"
    mock.field_value = "new_value_123"
    return mock

def test_alterar_nif_command_execute(mock_request_model):
    mock_request_model.intent = "alterar_nif"
    mock_request_model.field_value = "123456789"
    
    command = AlterarNifCommand()
    result = command.execute(mock_request_model)
    
    expected_result = {
        "action": "alterar_nif",
        "target_table": "TABELA_CLIENTES_CRM",
        "parameters": {"value": "123456789"},
        "where": {"client_id": "CRM_ID_PLACEHOLDER"}
    }
    assert result == expected_result

def test_alterar_morada_command_execute(mock_request_model):
    mock_request_model.intent = "alterar_morada"
    mock_request_model.field_value = "Rua do Ouro, 123"
    
    command = AlterarMoradaCommand()
    result = command.execute(mock_request_model)
    
    expected_result = {
        "action": "alterar_morada",
        "target_table": "TABELA_CLIENTES_CRM",
        "parameters": {"value": "Rua do Ouro, 123"},
        "where": {"client_id": "CRM_ID_PLACEHOLDER"}
    }
    assert result == expected_result

def test_default_simulation_command_execute(mock_request_model):
    command = DefaultSimulationCommand()
    result = command.execute(mock_request_model)
    
    assert result == {}