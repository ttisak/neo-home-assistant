"""The NEO Smartbox integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.typing import ConfigType

from . import frontend
from .const import DOMAIN, NEO_APP_COMMANDS, REMOTE_COMMANDS
from .coordinator import NeoSmartboxUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Add device_action platform
PLATFORMS: list[Platform] = [Platform.REMOTE]

CONFIG_SCHEMA = cv.removed(DOMAIN, raise_if_present=False)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): cv.string,
        vol.Required("action"): vol.In(NEO_APP_COMMANDS.keys()),
        vol.Required("long_press", default=False): cv.boolean,
    }
)

SERVICE_CUSTOM_ACTION = "remote_key_action"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the NEO Smartbox component."""
    # Initialize the domain data if not already there
    hass.data.setdefault(DOMAIN, {})

    await frontend.async_setup(hass)

    return True


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
    async def handle_custom_action(call: ServiceCall) -> None:
        """Handle the custom action service."""

        device_id: str | None = call.data.get("device_id", None)
        action_type: str | None = call.data.get("action", None)

        long_press: bool = call.data.get("long_press", False)

        if not device_id:
            _LOGGER.error("Device ID not found")
            return

        if not action_type:
            _LOGGER.error("Action type not found")
            return

        # Find the device's entry_id
        device_registry = dr.async_get(hass)
        device = device_registry.async_get(device_id)

        if not device:
            _LOGGER.error("Device not found in device registry")
            return

        _, box_device_id = next(iter(device.identifiers))

        await coordinator.api_client.send_key_action(
            device_id=box_device_id,
            key_name=REMOTE_COMMANDS[action_type],
            long_press=long_press,
            key_repeat=0,
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_CUSTOM_ACTION,
        handle_custom_action,
        schema=SERVICE_SCHEMA,
    )

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
