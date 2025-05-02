"""Support for NEO Smartbox remotes."""

from __future__ import annotations

from collections.abc import Iterable
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.remote import RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, REMOTE_COMMANDS
from .coordinator import NeoSmartboxUpdateCoordinator
from .models import NeoDeviceType, NeoSmartboxDevice

_LOGGER = logging.getLogger(__name__)

SERVICE_VOLUME_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required("long_press", default=False): cv.boolean,
        vol.Required("repeat", default=0): cv.positive_int,
    }
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up NEO Smartbox remote based on a config entry."""
    coordinator: NeoSmartboxUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [NeoSmartboxRemote(coordinator, device) for device in coordinator.data]

    async_add_entities(entities)


class NeoSmartboxRemote(CoordinatorEntity[NeoSmartboxUpdateCoordinator], RemoteEntity):
    """Representation of a NEO Smartbox remote."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: NeoSmartboxUpdateCoordinator, device: NeoSmartboxDevice
    ) -> None:
        """Initialize the NEO Smartbox remote."""
        super().__init__(coordinator)
        self._device = device
        self.device_id = device.id
        self._attr_unique_id = f"{DOMAIN}_{self.device_id}"
        self._attr_name = device.name
        self._attr_is_on = True
        # self._attr_commands_encoding = list(NEO_APP_COMMANDS.keys())

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": self._device.name,
            "manufacturer": "Telekom Slovenia",
            "model": "NEO Smartbox"
            if self._device.type == NeoDeviceType.STB
            else "NEO TV Lite",
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return True

    @property
    def commands(self) -> list[str]:
        """Return a list of supported commands."""
        return list(REMOTE_COMMANDS.keys())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific state attributes."""
        return {
            # "available_commands": list(NEO_APP_COMMANDS.keys()),
            # "command_descriptions": NEO_APP_COMMANDS,
            "device_id": self.device_id,
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        for device in self.coordinator.data:
            if device.id == self.device_id:
                self._device = device
                self._attr_is_on = True
                self._attr_current_activity = None
                break
        self.async_write_ha_state()

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send command to device."""
        # Extract optional parameters from kwargs
        long_press = kwargs.get("long_press", False)
        key_repeat = kwargs.get("repeat", 0)

        commands = list(command)
        if not commands:
            return

        for single_command in commands:
            if single_command in REMOTE_COMMANDS:
                api_command = REMOTE_COMMANDS[single_command]
                await self.coordinator.api_client.send_key_action(
                    device_id=self.device_id,
                    key_name=api_command,
                    long_press=long_press,
                    key_repeat=key_repeat,
                )
            else:
                _LOGGER.warning("Unsupported command: %s", single_command)
