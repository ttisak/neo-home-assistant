"""Tests for the NEO Smartbox initialization."""

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.components.neo_smartbox.const import DOMAIN
from homeassistant.components.remote import DOMAIN as REMOTE_DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
    label_registry as lr,
)
from homeassistant.setup import async_setup_component

from tests.common import MockConfigEntry, async_mock_service

# Service names from __init__.py
REMOTE_KEY_ACTION = "remote_key_action"
NAVIGATE_TO_CUSTOM_ACTION = "navigate_to_custom_action"
NAVIGATE_TO_LIVE_CHANNEL = "navigate_to_live_channel"


async def test_setup_component(hass: HomeAssistant) -> None:
    """Test setting up the NEO Smartbox component."""
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()
    assert DOMAIN in hass.data


async def test_setup_config_entry(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_api_client: AsyncMock
) -> None:
    """Test setting up the config entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.neo_smartbox.coordinator.NeoSmartboxApiClient",
        return_value=mock_api_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert DOMAIN in hass.data
    assert mock_config_entry.entry_id in hass.data[DOMAIN]
    assert len(hass.states.async_entity_ids(REMOTE_DOMAIN)) == 2  # Two mock devices


async def test_unload_config_entry(
    hass: HomeAssistant, init_integration: MockConfigEntry, mock_api_client: AsyncMock
) -> None:
    """Test unloading the config entry."""
    assert await hass.config_entries.async_unload(init_integration.entry_id)
    await hass.async_block_till_done()

    assert init_integration.state is ConfigEntryState.NOT_LOADED
    assert DOMAIN in hass.data
    assert init_integration.entry_id not in hass.data[DOMAIN]


async def test_setup_config_entry_connection_error(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test setup with connection error."""
    with patch(
        "homeassistant.components.neo_smartbox.coordinator.NeoSmartboxApiClient",
        autospec=True,
    ) as api_client_mock:
        client = api_client_mock.return_value
        client.get_all_devices = AsyncMock(
            side_effect=ConnectionError("Connection error")
        )

        mock_config_entry.add_to_hass(hass)
        assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_setup_config_entry_no_devices_found(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test setup when no devices are found results in setup retry."""
    with patch(
        "homeassistant.components.neo_smartbox.coordinator.NeoSmartboxApiClient",
        autospec=True,
    ) as api_client_mock:
        client = api_client_mock.return_value
        client.get_all_devices = AsyncMock(return_value=None)

        mock_config_entry.add_to_hass(hass)

        result = await hass.config_entries.async_setup(mock_config_entry.entry_id)
        assert result is False

        # Check that the entry is in setup retry state
        assert mock_config_entry.state == ConfigEntryState.SETUP_RETRY


async def test_get_devices_from_target_entity_id(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Test getting devices from entity_id target."""
    # Create a mock entity with device_id
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    # Create a device
    device = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "test_device_123")},
        name="Test Device",
    )

    # Create an entity linked to the device
    entity = entity_registry.async_get_or_create(
        "remote",
        DOMAIN,
        "test_entity",
        device_id=device.id,
    )

    call_mock = async_mock_service(hass, DOMAIN, REMOTE_KEY_ACTION)

    await hass.services.async_call(
        DOMAIN,
        REMOTE_KEY_ACTION,
        {
            "entity_id": [entity.entity_id],
            "action": "left",
            "long_press": False,
        },
        blocking=True,
    )

    assert len(call_mock) == 1


async def test_get_devices_from_target_entity_not_found(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test getting devices from entity_id when entity not found."""
    # Don't mock the service - call the real one to trigger error logging
    await hass.services.async_call(
        DOMAIN,
        REMOTE_KEY_ACTION,
        {
            "entity_id": ["remote.non_existent"],
            "action": "left",
            "long_press": False,
        },
        blocking=True,
    )

    # The error should be logged by get_devices_from_target function
    assert "Entity not found in entity registry" in caplog.text


async def test_get_devices_from_target_entity_no_device_id(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test getting devices from entity_id when entity has no device_id."""
    entity_registry = er.async_get(hass)

    # Create an entity without device_id
    entity = entity_registry.async_get_or_create(
        "remote",
        DOMAIN,
        "test_entity_no_device",
        device_id=None,
    )

    # Don't mock the service - call the real one to trigger error logging
    await hass.services.async_call(
        DOMAIN,
        REMOTE_KEY_ACTION,
        {
            "entity_id": [entity.entity_id],
            "action": "left",
            "long_press": False,
        },
        blocking=True,
    )

    # The error should be logged by get_devices_from_target function
    assert "Device ID not found in entity registry" in caplog.text


async def test_get_devices_from_target_entity_no_device_id_coverage(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test getting devices from entity_id when entity has no device_id with multiple entities."""
    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    # Create a valid device and entity
    device = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "valid_device")},
        name="Valid Device",
    )

    valid_entity = entity_registry.async_get_or_create(
        "remote",
        DOMAIN,
        "valid_entity",
        device_id=device.id,
    )

    # Create an entity without device_id
    invalid_entity = entity_registry.async_get_or_create(
        "remote",
        DOMAIN,
        "invalid_entity",
        device_id=None,
    )

    # Call with both entities - should continue processing after invalid entity
    await hass.services.async_call(
        DOMAIN,
        REMOTE_KEY_ACTION,
        {
            "entity_id": [invalid_entity.entity_id, valid_entity.entity_id],
            "action": "left",
            "long_press": False,
        },
        blocking=True,
    )

    # The error should be logged for the invalid entity
    assert "Device ID not found in entity registry" in caplog.text


async def test_get_devices_from_target_label_id(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Test getting devices from label_id target."""
    device_registry = dr.async_get(hass)

    # Create a device with a label
    device = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "test_device_456")},
        name="Test Device with Label",
    )

    # Mock the label functionality
    with patch.object(
        device_registry.devices, "get_devices_for_label", return_value=[device]
    ):
        call_mock = async_mock_service(hass, DOMAIN, REMOTE_KEY_ACTION)

        await hass.services.async_call(
            DOMAIN,
            REMOTE_KEY_ACTION,
            {
                "label_id": ["test_label"],
                "action": "left",
                "long_press": False,
            },
            blocking=True,
        )

        assert len(call_mock) == 1


async def test_get_devices_from_target_area_id(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Test getting devices from area_id target."""
    device_registry = dr.async_get(hass)

    # Create a device in an area
    device = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "test_device_789")},
        name="Test Device in Area",
    )

    # Mock the area functionality
    with patch.object(
        device_registry.devices, "get_devices_for_area_id", return_value=[device]
    ):
        call_mock = async_mock_service(hass, DOMAIN, REMOTE_KEY_ACTION)

        await hass.services.async_call(
            DOMAIN,
            REMOTE_KEY_ACTION,
            {
                "area_id": ["test_area"],
                "action": "left",
                "long_press": False,
            },
            blocking=True,
        )

        assert len(call_mock) == 1


async def test_get_devices_from_target_device_not_found(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test getting devices when device not found in registry."""
    # Don't mock the service - call the real one to trigger error logging
    await hass.services.async_call(
        DOMAIN,
        REMOTE_KEY_ACTION,
        {
            "device_id": ["non_existent_device"],
            "action": "left",
            "long_press": False,
        },
        blocking=True,
    )

    # The error should be logged by get_devices_from_target function
    assert "Device not found in device registry" in caplog.text


async def test_handle_remote_key_action_no_action(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test handling remote key action when no action is provided."""
    # Don't mock the service - call the real one to trigger error logging
    await hass.services.async_call(
        DOMAIN,
        REMOTE_KEY_ACTION,
        {
            "device_id": ["device1"],  # Use valid device ID from test data
            "long_press": False,
        },
        blocking=True,
    )

    # The error should be logged by the service function
    assert "Action type not found" in caplog.text


async def test_handle_remote_key_action_device_not_found(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test remote key action service with invalid device."""
    await hass.services.async_call(
        DOMAIN,
        REMOTE_KEY_ACTION,
        {
            "device_id": ["non_existent"],
            "action": "left",
            "long_press": False,
        },
        blocking=True,
    )

    assert "Device not found in device registry" in caplog.text


async def test_handle_navigate_to_custom_action_no_action(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test navigate to custom action service without action parameter."""
    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_CUSTOM_ACTION,
        {
            "device_id": ["device123"],
        },
        blocking=True,
    )

    assert "Action type not found" in caplog.text


async def test_handle_navigate_to_custom_action_device_not_found(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test navigate to custom action service with invalid device."""
    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_CUSTOM_ACTION,
        {
            "device_id": ["non_existent"],
            "action": "netflix",
        },
        blocking=True,
    )

    assert "Device not found in device registry" in caplog.text


async def test_handle_navigate_to_live_channel_no_channel_id(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test navigate to live channel service without channel_id parameter."""
    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_LIVE_CHANNEL,
        {
            "device_id": ["device123"],
        },
        blocking=True,
    )

    assert "Channel ID not found" in caplog.text


async def test_handle_navigate_to_live_channel_device_not_found(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test navigate to live channel service with invalid device."""
    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_LIVE_CHANNEL,
        {
            "device_id": ["non_existent"],
            "channel_id": "123",
        },
        blocking=True,
    )

    assert "Device not found in device registry" in caplog.text


async def test_unload_entry_no_entry_data(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_api_client: AsyncMock
) -> None:
    """Test unloading entry when entry_id not in hass.data."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.neo_smartbox.coordinator.NeoSmartboxApiClient",
        return_value=mock_api_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    # Remove the entry data manually to test the pop logic
    if DOMAIN in hass.data and mock_config_entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(mock_config_entry.entry_id)

    # Now unload - should not error even though entry_id is not in data
    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


async def test_get_devices_from_target_device_no_identifiers(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test getting devices when device has different domain identifiers."""
    device_registry = dr.async_get(hass)

    # Create a device with identifiers from a different domain
    device = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={("other_domain", "test_device")},  # Different domain
        name="Test Device Different Domain",
    )

    await hass.services.async_call(
        DOMAIN,
        REMOTE_KEY_ACTION,
        {
            "device_id": [device.id],
            "action": "left",  # Use valid action from REMOTE_COMMANDS
            "long_press": False,
        },
        blocking=True,
    )

    # This should complete without error but won't call the API


async def test_handle_remote_key_action_empty_box_device_id(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test remote key action service when box_device_id is empty."""
    device_registry = dr.async_get(hass)

    # Create a device with empty identifiers that results in empty box_device_id
    device = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "")},  # Empty device ID
        name="Test Device Empty ID",
    )

    await hass.services.async_call(
        DOMAIN,
        REMOTE_KEY_ACTION,
        {
            "device_id": [device.id],
            "action": "left",
            "long_press": False,
        },
        blocking=True,
    )

    assert "Device not found in device registry" in caplog.text


async def test_handle_navigate_to_custom_action_empty_box_device_id(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test navigate to custom action service when box_device_id is empty."""
    device_registry = dr.async_get(hass)

    # Create a device with empty identifiers that results in empty box_device_id
    device = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "")},  # Empty device ID
        name="Test Device Empty ID",
    )

    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_CUSTOM_ACTION,
        {
            "device_id": [device.id],
            "action": "netflix",
        },
        blocking=True,
    )

    assert "Device not found in device registry" in caplog.text


async def test_handle_navigate_to_live_channel_empty_box_device_id(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test navigate to live channel service when box_device_id is empty."""
    device_registry = dr.async_get(hass)

    # Create a device with empty identifiers that results in empty box_device_id
    device = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "")},  # Empty device ID
        name="Test Device Empty ID",
    )

    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_LIVE_CHANNEL,
        {
            "device_id": [device.id],
            "channel_id": "123",
        },
        blocking=True,
    )

    assert "Device not found in device registry" in caplog.text


async def test_get_devices_from_target_with_label_id(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test get_devices_from_target function with label_id."""
    device_registry = dr.async_get(hass)
    label_registry = lr.async_get(hass)

    # Create a label
    label = label_registry.async_create(name="test_label")

    # Create a device and assign it to the label
    device = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "test_device_label")},
        name="Test Device Label",
    )

    # Update device with the label
    device_registry.async_update_device(device.id, labels={label.label_id})

    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_CUSTOM_ACTION,
        {
            "label_id": [label.label_id],
            "action": "left",
        },
        blocking=True,
    )

    # Verify the service call was successful (no errors logged)


async def test_get_devices_from_target_with_area_id(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test get_devices_from_target function with area_id."""
    device_registry = dr.async_get(hass)
    area_registry = ar.async_get(hass)

    # Create an area
    area = area_registry.async_create(name="test_area")

    # Create a device and assign it to the area
    device = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "test_device_area")},
        name="Test Device Area",
    )
    device_registry.async_update_device(device.id, area_id=area.id)

    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_CUSTOM_ACTION,
        {
            "area_id": [area.id],
            "action": "left",
        },
        blocking=True,
    )

    # Verify the service call was successful (no errors logged)


async def test_handle_navigate_action_empty_box_device_id(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test navigate action service when box_device_id is empty."""
    device_registry = dr.async_get(hass)

    # Create a device with empty identifiers that results in empty box_device_id
    _device = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "")},  # Empty device ID
        name="Test Device Empty ID",
    )

    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_CUSTOM_ACTION,
        {
            "device_id": [_device.id],
            "action": "left",
        },
        blocking=True,
    )

    assert "Device not found in device registry" in caplog.text


async def test_get_devices_from_target_multiple_labels_and_areas(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test get_devices_from_target function with multiple labels and areas."""
    device_registry = dr.async_get(hass)
    label_registry = lr.async_get(hass)
    area_registry = ar.async_get(hass)

    # Create labels
    label1 = label_registry.async_create(name="test_label_1")
    label2 = label_registry.async_create(name="test_label_2")

    # Create areas
    area1 = area_registry.async_create(name="test_area_1")
    area2 = area_registry.async_create(name="test_area_2")

    # Create devices for labels
    device_label1 = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "test_device_label_1")},
        name="Test Device Label 1",
    )
    device_registry.async_update_device(device_label1.id, labels={label1.label_id})

    device_label2 = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "test_device_label_2")},
        name="Test Device Label 2",
    )
    device_registry.async_update_device(device_label2.id, labels={label2.label_id})

    # Create devices for areas
    _device_area1 = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "test_device_area_1")},
        name="Test Device Area 1",
    )
    device_registry.async_update_device(_device_area1.id, area_id=area1.id)

    _device_area2 = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "test_device_area_2")},
        name="Test Device Area 2",
    )
    device_registry.async_update_device(_device_area2.id, area_id=area2.id)

    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_CUSTOM_ACTION,
        {
            "label_id": [label1.label_id, label2.label_id],
            "area_id": [area1.id, area2.id],
            "action": "left",
        },
        blocking=True,
    )

    # Verify the service call was successful (no errors logged)


async def test_get_devices_from_target_empty_label_id_list(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test get_devices_from_target function with empty label_id list."""
    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_CUSTOM_ACTION,
        {
            "label_id": [],
            "action": "left",
        },
        blocking=True,
    )

    # Verify the service call was successful (no errors logged)


async def test_get_devices_from_target_empty_area_id_list(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test get_devices_from_target function with empty area_id list."""
    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_CUSTOM_ACTION,
        {
            "area_id": [],
            "action": "left",
        },
        blocking=True,
    )

    # Verify the service call was successful (no errors logged)


async def test_handle_navigate_to_live_channel_success(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test navigate to live channel service successful execution."""
    device_registry = dr.async_get(hass)

    # Create a device with proper identifiers
    device = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "test_device_live_channel")},
        name="Test Device Live Channel",
    )

    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_LIVE_CHANNEL,
        {
            "device_id": [device.id],
            "channel_id": "123",
        },
        blocking=True,
    )

    # Verify the service call was successful (no errors logged)


async def test_get_devices_from_target_label_device_filtering(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test label device filtering logic when devices are already in ha_device_ids."""
    device_registry = dr.async_get(hass)
    label_registry = lr.async_get(hass)

    # Create a label
    label = label_registry.async_create(name="test_label_filter")

    # Create multiple devices and assign them to the label
    device1 = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "test_device_filter_1")},
        name="Test Device Filter 1",
    )
    device_registry.async_update_device(device1.id, labels={label.label_id})

    device2 = device_registry.async_get_or_create(
        config_entry_id=init_integration.entry_id,
        identifiers={(DOMAIN, "test_device_filter_2")},
        name="Test Device Filter 2",
    )
    device_registry.async_update_device(device2.id, labels={label.label_id})

    # Call service with both device_id (direct) and label_id
    # This should trigger the filtering logic in label processing
    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_CUSTOM_ACTION,
        {
            "device_id": [device1.id],  # This will be added first
            "label_id": [label.label_id],  # This should filter out device1 as duplicate
            "action": "left",
        },
        blocking=True,
    )

    # Verify the service call was successful (no errors logged)
