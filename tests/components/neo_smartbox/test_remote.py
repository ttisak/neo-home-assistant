"""Tests for the NEO Smartbox remote platform."""

from unittest.mock import AsyncMock

from homeassistant.components.neo_smartbox.const import DOMAIN
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
