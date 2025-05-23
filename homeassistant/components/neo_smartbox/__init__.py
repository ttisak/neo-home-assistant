"""The NEO Smartbox integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import (
    config_validation as cv,
    device_registry as dr,
    entity_registry as er,
)
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.read_only_dict import ReadOnlyDict

from . import frontend
from .const import DOMAIN, REMOTE_COMMANDS
from .coordinator import NeoSmartboxUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Add device_action platform
PLATFORMS: list[Platform] = [Platform.REMOTE]

CONFIG_SCHEMA = cv.removed(DOMAIN, raise_if_present=False)

REMOTE_KEY_ACTION = "remote_key_action"
NAVIGATE_TO_LIVE_CHANNEL = "navigate_to_live_channel"
NAVIGATE_TO_CUSTOM_ACTION = "navigate_to_custom_action"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the NEO Smartbox component."""
    # Initialize the domain data if not already there
    hass.data.setdefault(DOMAIN, {})

    await frontend.async_setup(hass)

    return True


def get_devices_from_target(
    hass: HomeAssistant, data: ReadOnlyDict[str, Any]
) -> list[str]:
    """Get devices from target."""

    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    ha_device_ids = data.get("device_id", [])

    for entity_id in data.get("entity_id", []):
        entry = entity_registry.async_get(entity_id)

        if not entry:
            _LOGGER.error("Entity not found in entity registry")
            continue

        ha_device_id = entry.device_id
        if not ha_device_id:
            _LOGGER.error("Device ID not found in entity registry")
            continue

        ha_device_ids.append(ha_device_id)

    for label_id in data.get("label_id", []):
        ha_devices = device_registry.devices.get_devices_for_label(label_id)

        device_ids = [
            device.id for device in ha_devices if device.id not in ha_device_ids
        ]

        ha_device_ids.extend(device_ids)

    for area_id in data.get("area_id", []):
        ha_devices = device_registry.devices.get_devices_for_area_id(area_id)

        device_ids = [
            device.id for device in ha_devices if device.id not in ha_device_ids
        ]

        ha_device_ids.extend(device_ids)

    box_device_ids = []

    for device_id in ha_device_ids:
        device = device_registry.async_get(device_id)

        if not device:
            _LOGGER.error("Device not found in device registry")
            continue

        _, box_device_id = next(iter(device.identifiers))

        if box_device_id not in box_device_ids:
            box_device_ids.append(box_device_id)

    return box_device_ids


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NEO Smartbox from a config entry."""
    # Initialize runtime_data if not already set

    api_key = entry.data[CONF_API_KEY]

    coordinator = NeoSmartboxUpdateCoordinator(hass, api_key)

    entry.runtime_data = coordinator

    await coordinator.async_config_entry_first_refresh()

    if not coordinator.data:
        raise ConfigEntryNotReady("No devices found")

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Register device actions service
    async def handle_remote_key_action(call: ServiceCall) -> None:
        """Handle the custom action service."""

        action_type: str | None = call.data.get("action", None)

        long_press: bool = call.data.get("long_press", False)

        if not action_type:
            _LOGGER.error("Action type not found")
            return

        box_device_ids = get_devices_from_target(hass, call.data)

        for box_device_id in box_device_ids:
            if not box_device_id:
                _LOGGER.error("Device not found in device registry")
                return

            await coordinator.api_client.send_key_action(
                device_id=box_device_id,
                key_name=REMOTE_COMMANDS[action_type],
                long_press=long_press,
                key_repeat=0,
            )

    async def handle_navigate_to_custom_action(call: ServiceCall) -> None:
        """Handle the navigation to provided action."""

        action_type: str | None = call.data.get("action", None)

        if not action_type:
            _LOGGER.error("Action type not found")
            return

        box_device_ids = get_devices_from_target(hass, call.data)

        for box_device_id in box_device_ids:
            if not box_device_id:
                _LOGGER.error("Device not found in device registry")
                return

            await coordinator.api_client.navigate_action(
                device_id=box_device_id,
                action=action_type,
            )

    async def handle_navigate_to_live_channel(call: ServiceCall) -> None:
        """Handle the navigation to provided action."""

        channel_id: str | None = call.data.get("channel_id", None)

        if not channel_id:
            _LOGGER.error("Channel ID not found")
            return

        box_device_ids = get_devices_from_target(hass, call.data)

        for box_device_id in box_device_ids:
            if not box_device_id:
                _LOGGER.error("Device not found in device registry")
                return

            await coordinator.api_client.navigate_action(
                device_id=box_device_id,
                action=f"app://player/livetv/id/{channel_id}",
            )

    hass.services.async_register(
        DOMAIN,
        REMOTE_KEY_ACTION,
        handle_remote_key_action,
    )

    hass.services.async_register(
        DOMAIN,
        NAVIGATE_TO_CUSTOM_ACTION,
        handle_navigate_to_custom_action,
    )

    hass.services.async_register(
        DOMAIN,
        NAVIGATE_TO_LIVE_CHANNEL,
        handle_navigate_to_live_channel,
    )

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Pop the entry_id if it exists, otherwise just continue
        if entry.entry_id in hass.data.get(DOMAIN, {}):
            hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
