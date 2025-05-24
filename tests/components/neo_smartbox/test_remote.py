"""Tests for the NEO Smartbox remote platform."""

from unittest.mock import AsyncMock

import pytest

from homeassistant.components.neo_smartbox.const import DOMAIN, REMOTE_COMMANDS
from homeassistant.components.neo_smartbox.remote import NeoSmartboxRemote
from homeassistant.components.remote import (
    ATTR_COMMAND,
    DOMAIN as REMOTE_DOMAIN,
    SERVICE_SEND_COMMAND,
)
from homeassistant.const import ATTR_DEVICE_ID, ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

# pylint: disable=unused-import
from .test_data import DEVICE_DATA, SMART_TV_DEVICE_ID, STB_DEVICE_ID

# Entity IDs for the two test devices
STB_ENTITY_ID = f"{REMOTE_DOMAIN}.living_room_box_living_room_box"
SMART_TV_ENTITY_ID = f"{REMOTE_DOMAIN}.bedroom_tv_bedroom_tv"


async def test_setup(hass: HomeAssistant, init_integration) -> None:
    """Test setup with basic config."""
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    # Verify entities are created
    assert hass.states.get(STB_ENTITY_ID)
    assert hass.states.get(SMART_TV_ENTITY_ID)

    # Check entity registry entries
    stb_entry = entity_registry.async_get(STB_ENTITY_ID)
    smart_tv_entry = entity_registry.async_get(SMART_TV_ENTITY_ID)

    assert stb_entry
    assert smart_tv_entry

    # Check device registry entries
    stb_device = device_registry.async_get_device({(DOMAIN, STB_DEVICE_ID)})
    smart_tv_device = device_registry.async_get_device({(DOMAIN, SMART_TV_DEVICE_ID)})

    assert stb_device
    assert smart_tv_device

    assert stb_device.name == DEVICE_DATA[0].name
    assert smart_tv_device.name == DEVICE_DATA[1].name


async def test_unique_id(
    hass: HomeAssistant, entity_registry: er.EntityRegistry, init_integration
) -> None:
    """Test unique id."""
    stb_entity = entity_registry.async_get(STB_ENTITY_ID)
    smart_tv_entity = entity_registry.async_get(SMART_TV_ENTITY_ID)

    # Unique ID is neo_smartbox_<device_id>
    assert stb_entity.unique_id == f"{DOMAIN}_{STB_DEVICE_ID}"
    assert smart_tv_entity.unique_id == f"{DOMAIN}_{SMART_TV_DEVICE_ID}"


async def test_send_command(
    hass: HomeAssistant, init_integration, mock_api_client: AsyncMock
) -> None:
    """Test the send command service."""
    await hass.services.async_call(
        REMOTE_DOMAIN,
        SERVICE_SEND_COMMAND,
        {
            ATTR_ENTITY_ID: STB_ENTITY_ID,
            ATTR_COMMAND: ["home"],
        },
        blocking=True,
    )

    mock_api_client.send_key_action.assert_called_once_with(
        device_id=STB_DEVICE_ID,
        key_name="Home",
        long_press=False,
        key_repeat=0,
    )

    # Reset mock
    mock_api_client.send_key_action.reset_mock()

    # Test with another command
    await hass.services.async_call(
        REMOTE_DOMAIN,
        SERVICE_SEND_COMMAND,
        {
            ATTR_ENTITY_ID: STB_ENTITY_ID,
            ATTR_COMMAND: ["volume_up"],
        },
        blocking=True,
    )

    mock_api_client.send_key_action.assert_called_once_with(
        device_id=STB_DEVICE_ID,
        key_name="VolumeUp",
        long_press=False,
        key_repeat=0,
    )


async def test_navigate_to_live_channel_service(
    hass: HomeAssistant, init_integration, mock_api_client: AsyncMock
) -> None:
    """Test the navigate to live channel service."""
    # Get the device ID
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device({(DOMAIN, STB_DEVICE_ID)})

    await hass.services.async_call(
        DOMAIN,
        "navigate_to_live_channel",
        {
            ATTR_DEVICE_ID: [device.id],
            "channel_id": "channel123",
        },
        blocking=True,
    )

    # The implementation should call navigate_action with appropriate parameters
    mock_api_client.navigate_action.assert_called_once_with(
        device_id=STB_DEVICE_ID,
        action="app://player/livetv/id/channel123",
    )


async def test_navigate_to_custom_action_service(
    hass: HomeAssistant, init_integration, mock_api_client: AsyncMock
) -> None:
    """Test the navigate to custom action service."""
    # Get the device ID
    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device({(DOMAIN, STB_DEVICE_ID)})

    await hass.services.async_call(
        DOMAIN,
        "navigate_to_custom_action",
        {
            ATTR_DEVICE_ID: [device.id],
            "action": "some_action",
        },
        blocking=True,
    )

    # The implementation should call navigate_action with appropriate parameters
    mock_api_client.navigate_action.assert_called_once_with(
        device_id=STB_DEVICE_ID,
        action="some_action",
    )


async def test_send_command_empty_list(
    hass: HomeAssistant, init_integration, mock_api_client: AsyncMock
) -> None:
    """Test send command with empty command list."""
    await hass.services.async_call(
        REMOTE_DOMAIN,
        SERVICE_SEND_COMMAND,
        {
            ATTR_ENTITY_ID: STB_ENTITY_ID,
            ATTR_COMMAND: [],  # Empty command list
        },
        blocking=True,
    )

    # Should not call the API when commands are empty
    mock_api_client.send_key_action.assert_not_called()


async def test_send_command_unsupported(
    hass: HomeAssistant,
    init_integration,
    mock_api_client: AsyncMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test send command with unsupported command."""
    await hass.services.async_call(
        REMOTE_DOMAIN,
        SERVICE_SEND_COMMAND,
        {
            ATTR_ENTITY_ID: STB_ENTITY_ID,
            ATTR_COMMAND: ["unsupported_command"],
        },
        blocking=True,
    )

    # Should not call the API for unsupported commands
    mock_api_client.send_key_action.assert_not_called()
    # Should log a warning
    assert "Unsupported command: unsupported_command" in caplog.text


async def test_send_command_with_kwargs(
    hass: HomeAssistant, init_integration, mock_api_client: AsyncMock
) -> None:
    """Test send command with optional kwargs."""
    await hass.services.async_call(
        REMOTE_DOMAIN,
        SERVICE_SEND_COMMAND,
        {
            ATTR_ENTITY_ID: STB_ENTITY_ID,
            ATTR_COMMAND: ["home"],
            "hold_secs": 1.0,
            "num_repeats": 3,
        },
        blocking=True,
    )

    mock_api_client.send_key_action.assert_called_once_with(
        device_id=STB_DEVICE_ID,
        key_name="Home",
        long_press=False,
        key_repeat=0,
    )


async def test_coordinator_update_device_not_found(
    hass: HomeAssistant, init_integration, mock_api_client: AsyncMock
) -> None:
    """Test coordinator update when device is not found in data."""
    # Get the coordinator
    coordinator = hass.data[DOMAIN][init_integration.entry_id]

    # Save original data
    original_data = coordinator.data

    # Simulate coordinator data update without our device
    coordinator.data = []  # Empty device list

    # Trigger update to test the scenario where device is missing
    await coordinator.async_refresh()

    # Restore original data
    coordinator.data = original_data

    # The update should complete without error


async def test_extra_state_attributes(hass: HomeAssistant, init_integration) -> None:
    """Test extra state attributes property."""
    # Get the entity state
    state = hass.states.get(STB_ENTITY_ID)
    assert state is not None

    # Check that the entity has the device_id attribute
    assert "device_id" in state.attributes
    assert state.attributes["device_id"] == STB_DEVICE_ID


async def test_commands_property(hass: HomeAssistant, init_integration) -> None:
    """Test the commands property returns supported commands."""

    # Get the entity from the entity registry
    entity_registry = er.async_get(hass)
    stb_entry = entity_registry.async_get(STB_ENTITY_ID)
    assert stb_entry is not None

    # Get the actual entity instance
    entity = hass.data[DOMAIN][init_integration.entry_id]

    # Find the remote entity for our STB device
    remote_entity = None
    for device in entity.data:
        if device.id == STB_DEVICE_ID:
            # Get the remote entity
            remote_entity = NeoSmartboxRemote(entity, device)
            break

    assert remote_entity is not None

    # Test that the commands property returns the expected list
    commands = remote_entity.commands
    expected_commands = list(REMOTE_COMMANDS.keys())

    assert isinstance(commands, list)
    assert commands == expected_commands
    assert len(commands) == len(REMOTE_COMMANDS)

    # Verify some expected commands are present
    assert "power" in commands
    assert "up" in commands
    assert "down" in commands
    assert "left" in commands
    assert "right" in commands
    assert "ok" in commands
    assert "home" in commands
    assert "back" in commands
    assert "volume_up" in commands
    assert "volume_down" in commands
