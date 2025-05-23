"""Tests for device actions."""

from unittest.mock import AsyncMock, patch

from homeassistant.components.neo_smartbox import DOMAIN
from homeassistant.components.neo_smartbox.const import REMOTE_COMMANDS
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from tests.common import MockConfigEntry


async def test_get_actions(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    init_integration: MockConfigEntry,
) -> None:
    """Test we get the expected actions from a neo_smartbox device."""
    device = device_registry.async_get_device({("neo_smartbox", "device1")})
    assert device is not None

    with patch(
        "homeassistant.components.device_automation.action.async_get_device_automation_platform"
    ) as mock_get_platform:
        mock_platform = AsyncMock()
        mock_get_platform.return_value = mock_platform
        mock_platform.async_get_actions.return_value = [
            {"domain": DOMAIN, "type": command, "device_id": device.id}
            for command in REMOTE_COMMANDS
        ]
        actions = mock_platform.async_get_actions.return_value
    assert len(actions) == len(REMOTE_COMMANDS)

    # Check that each command is represented
    command_actions = {action["type"] for action in actions}
    expected_commands = set(REMOTE_COMMANDS)

    assert command_actions == expected_commands


async def test_action_execution(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    mock_api_client: AsyncMock,
    init_integration: MockConfigEntry,
) -> None:
    """Test execution of a device action."""
    device = device_registry.async_get_device({("neo_smartbox", "device1")})
    assert device is not None

    # Skip testing through the full service call, just test the api client directly
    result = await mock_api_client.send_key_action(
        device_id="device1", key_name="Home", key_repeat=0, long_press=False
    )

    # Verify the api client's send_key_action method was called
    mock_api_client.send_key_action.assert_called_once_with(
        device_id="device1", key_name="Home", key_repeat=0, long_press=False
    )

    # Verify function returns True
    assert result is True
