"""The NEO Smartbox integration."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    ConfigEntryError,
    ConfigEntryNotReady,
)
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

# For your initial PR, limit it to 1 platform.
_PLATFORMS: list[Platform] = [Platform.LIGHT]

CONFIG_SCHEMA = cv.removed(DOMAIN, raise_if_present=False)


type New_NameConfigEntry = config_entries.ConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Set up my integration from a config entry."""

    a = 1
    if a > 2:
        raise ConfigEntryNotReady("Device is offline")
    if a > 2:
        raise ConfigEntryAuthFailed("Invalid authentication")
    if a > 2:
        raise ConfigEntryError("Account closed")

    entry.runtime_data = {}

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: New_NameConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
