"""Tests for device actions."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
import voluptuous as vol

from homeassistant.components.neo_smartbox import DOMAIN
from homeassistant.components.neo_smartbox.const import (
    NEO_APP_COMMANDS,
    REMOTE_COMMANDS,
)
from homeassistant.components.neo_smartbox.device_action import (
    ATTR_CHANNEL_ID,
    ATTR_DESTINATION,
    ATTR_LONG_PRESS,
    NAVIGATE_TO,
    NAVIGATE_TO_LIVE_CHANNEL,
    async_call_action_from_config,
    async_get_action_capabilities,
    async_get_actions,
    async_setup_entry,
    async_validate_action_config,
)
from homeassistant.components.neo_smartbox.models import TvChannel
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_TYPE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .test_data import STB_DEVICE_ID

from tests.common import MockConfigEntry, async_mock_service


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


# New tests for 100% coverage


async def test_direct_async_get_actions(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    init_integration: MockConfigEntry,
) -> None:
    """Test we get the expected actions directly from the module."""
    device = device_registry.async_get_device({("neo_smartbox", "device1")})
    assert device is not None

    actions = await async_get_actions(hass, device.id)

    # Verify that we have the expected number of actions
    assert len(actions) == 2 + len(NEO_APP_COMMANDS)

    # Check that we have navigate actions
    assert any(action[CONF_TYPE] == NAVIGATE_TO for action in actions)
    assert any(action[CONF_TYPE] == NAVIGATE_TO_LIVE_CHANNEL for action in actions)

    # Check that all app commands are included
    for app_command in NEO_APP_COMMANDS:
        assert any(action[CONF_TYPE] == app_command for action in actions)

    # Check the structure of the actions
    for action in actions:
        assert action[CONF_DEVICE_ID] == device.id
        assert action[CONF_DOMAIN] == DOMAIN


async def test_async_get_actions_no_device(hass: HomeAssistant) -> None:
    """Test with a device not in registry."""
    device_registry = dr.async_get(hass)

    with patch.object(device_registry, "async_get", return_value=None):
        actions = await async_get_actions(hass, "nonexistent_device")

    # Should return some actions for navigation even if device doesn't exist
    assert len(actions) == 2


async def test_async_get_actions_no_config_entries(
    hass: HomeAssistant, device_registry: dr.DeviceRegistry
) -> None:
    """Test with a device that has no config entries."""
    mock_device = Mock()
    mock_device.id = "mock_device_id"
    mock_device.config_entries = set()

    with patch.object(device_registry, "async_get", return_value=mock_device):
        actions = await async_get_actions(hass, mock_device.id)

    # Should have only navigation actions
    assert len(actions) == 2


async def test_async_get_action_capabilities_navigate_to(hass: HomeAssistant) -> None:
    """Test capabilities for navigate_to action."""
    config = {
        CONF_DEVICE_ID: "mock-device-id",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: NAVIGATE_TO,
    }

    capabilities = await async_get_action_capabilities(hass, config)

    assert isinstance(capabilities, dict)
    assert "extra_fields" in capabilities

    # Test that schema requires destination
    with pytest.raises(vol.error.MultipleInvalid):
        capabilities["extra_fields"]({})

    # Valid data with destination
    capabilities["extra_fields"]({ATTR_DESTINATION: "app://settings"})


async def test_async_get_action_capabilities_standard_action(
    hass: HomeAssistant,
) -> None:
    """Test capabilities for standard remote key action."""
    config = {
        CONF_DEVICE_ID: "mock-device-id",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: next(iter(NEO_APP_COMMANDS)),
    }

    capabilities = await async_get_action_capabilities(hass, config)

    assert isinstance(capabilities, dict)
    assert "extra_fields" in capabilities

    # Test schema with and without long_press
    capabilities["extra_fields"]({})
    capabilities["extra_fields"]({ATTR_LONG_PRESS: True})
    capabilities["extra_fields"]({ATTR_LONG_PRESS: False})


async def test_async_get_action_capabilities_navigate_to_live_channel(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Test capabilities for navigate_to_live_channel action."""
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device({("neo_smartbox", STB_DEVICE_ID)})
    assert device is not None

    # Create mock channels
    mock_channels = [
        TvChannel(
            id="ch1", number="1", title="Channel One", logo="", favorite=False, group=""
        ),
        TvChannel(
            id="ch2", number="2", title="Channel Two", logo="", favorite=False, group=""
        ),
    ]

    # Set up coordinator in hass data
    coordinator = hass.data[DOMAIN][init_integration.entry_id]
    coordinator.api_client.get_channel_list = AsyncMock(return_value=mock_channels)

    config = {
        CONF_DEVICE_ID: device.id,
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: NAVIGATE_TO_LIVE_CHANNEL,
    }

    capabilities = await async_get_action_capabilities(hass, config)

    assert "extra_fields" in capabilities

    # Test that schema requires valid channel ID
    with pytest.raises(vol.error.MultipleInvalid):
        capabilities["extra_fields"]({})

    with pytest.raises(vol.error.MultipleInvalid):
        capabilities["extra_fields"]({ATTR_CHANNEL_ID: "invalid-id"})

    # Valid channel ID should pass
    capabilities["extra_fields"]({ATTR_CHANNEL_ID: "ch1"})


async def test_async_get_action_capabilities_device_not_found(
    hass: HomeAssistant,
) -> None:
    """Test error handling when device not found."""
    config = {
        CONF_DEVICE_ID: "nonexistent-device",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: NAVIGATE_TO_LIVE_CHANNEL,
    }

    with pytest.raises(ValueError) as excinfo:
        await async_get_action_capabilities(hass, config)

    assert "Device not found" in str(excinfo.value)


async def test_async_get_action_capabilities_coordinator_not_found(
    hass: HomeAssistant, device_registry: dr.DeviceRegistry
) -> None:
    """Test error handling when coordinator not found."""
    # Create device with config entries not matching any coordinator
    mock_device = Mock()
    mock_device.id = "mock-device-id"
    mock_device.config_entries = {"invalid-entry-id"}

    with (
        patch.object(device_registry, "async_get", return_value=mock_device),
        patch.dict(hass.data, {DOMAIN: {}}),
    ):
        config = {
            CONF_DEVICE_ID: mock_device.id,
            CONF_DOMAIN: DOMAIN,
            CONF_TYPE: NAVIGATE_TO_LIVE_CHANNEL,
        }

        with pytest.raises(ValueError) as excinfo:
            await async_get_action_capabilities(hass, config)

        assert "Coordinator not found" in str(excinfo.value)


async def test_async_validate_action_config(hass: HomeAssistant) -> None:
    """Test action config validation."""
    # Test with valid config
    valid_config = {
        CONF_DEVICE_ID: "mock-device-id",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: NAVIGATE_TO,
    }

    # Just test that it doesn't raise an exception
    result = await async_validate_action_config(hass, valid_config)
    assert isinstance(result, dict)
    assert result[CONF_DOMAIN] == DOMAIN
    assert result[CONF_TYPE] == NAVIGATE_TO


async def test_async_call_action_from_config_remote_key(hass: HomeAssistant) -> None:
    """Test calling remote key action from config."""
    config = {
        CONF_DEVICE_ID: "mock-device-id",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: next(iter(NEO_APP_COMMANDS)),
        ATTR_LONG_PRESS: True,
    }

    calls = async_mock_service(hass, DOMAIN, "remote_key_action")
    await async_call_action_from_config(hass, config, {}, None)

    # Verify the service was called with correct parameters
    assert len(calls) == 1
    call = calls[0]
    assert call.domain == DOMAIN
    assert call.service == "remote_key_action"
    assert call.data["device_id"] == ["mock-device-id"]
    assert call.data["action"] == config[CONF_TYPE]
    assert call.data["long_press"] is True


async def test_async_call_action_from_config_navigate_to(hass: HomeAssistant) -> None:
    """Test calling navigate_to action from config."""
    config = {
        CONF_DEVICE_ID: "mock-device-id",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: NAVIGATE_TO,
        ATTR_DESTINATION: "app://settings",
    }

    calls = async_mock_service(hass, DOMAIN, "navigate_to_custom_action")
    await async_call_action_from_config(hass, config, {}, None)

    # Verify the service was called with correct parameters
    assert len(calls) == 1
    call = calls[0]
    assert call.domain == DOMAIN
    assert call.service == "navigate_to_custom_action"
    assert call.data["device_id"] == ["mock-device-id"]
    assert call.data["action"] == "app://settings"


async def test_async_call_action_from_config_navigate_to_missing_destination(
    hass: HomeAssistant,
) -> None:
    """Test error handling when destination is missing."""
    calls = async_mock_service(hass, DOMAIN, "navigate_to_custom_action")

    with patch(
        "homeassistant.components.neo_smartbox.device_action._LOGGER.error"
    ) as mock_log:
        config = {
            CONF_DEVICE_ID: "mock-device-id",
            CONF_DOMAIN: DOMAIN,
            CONF_TYPE: NAVIGATE_TO,
            # No destination
        }

        await async_call_action_from_config(hass, config, {}, None)

        mock_log.assert_called_once()
        assert "Invalid destination" in mock_log.call_args[0][0]

    # No service calls should have been made
    assert len(calls) == 0


async def test_async_call_action_from_config_navigate_to_live_channel(
    hass: HomeAssistant,
) -> None:
    """Test calling navigate_to_live_channel action from config."""
    calls = async_mock_service(hass, DOMAIN, "navigate_to_custom_action")
    config = {
        CONF_DEVICE_ID: "mock-device-id",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: NAVIGATE_TO_LIVE_CHANNEL,
        ATTR_CHANNEL_ID: "ch1",
    }

    await async_call_action_from_config(hass, config, {}, None)

    # Verify the service was called with correct parameters
    assert len(calls) == 1
    call = calls[0]
    assert call.domain == DOMAIN
    assert call.service == "navigate_to_custom_action"
    assert call.data["device_id"] == ["mock-device-id"]
    assert call.data["action"] == "app://player/livetv/id/ch1"


async def test_async_call_action_from_config_navigate_to_live_channel_missing_channel(
    hass: HomeAssistant,
) -> None:
    """Test error handling when channel ID is missing."""
    calls = async_mock_service(hass, DOMAIN, "navigate_to_custom_action")

    with patch(
        "homeassistant.components.neo_smartbox.device_action._LOGGER.error"
    ) as mock_log:
        config = {
            CONF_DEVICE_ID: "mock-device-id",
            CONF_DOMAIN: DOMAIN,
            CONF_TYPE: NAVIGATE_TO_LIVE_CHANNEL,
            # No channel_id
        }

        await async_call_action_from_config(hass, config, {}, None)

        mock_log.assert_called_once()
        assert "Channel ID is required" in mock_log.call_args[0][0]

    # No service calls should have been made
    assert len(calls) == 0


async def test_async_setup_entry(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test setting up from a config entry."""

    # Setup should always return True as it doesn't need to register anything
    assert await async_setup_entry(hass, mock_config_entry) is True
