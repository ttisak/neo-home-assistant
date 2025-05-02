# Create a new file: device_action.py
"""Provides device actions for NEO Smartbox."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.device_automation import async_validate_entity_schema
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_TYPE
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.typing import ConfigType, TemplateVarsType

from . import DOMAIN, SERVICE_CUSTOM_ACTION
from .const import NEO_APP_COMMANDS

_LOGGER = logging.getLogger(__name__)

ACTION_TYPES = list(NEO_APP_COMMANDS.keys())

CONF_LONG_PRESS = "long_press"

ACTION_SCHEMA = cv.DEVICE_ACTION_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(ACTION_TYPES),
        vol.Optional(CONF_LONG_PRESS, default=False): cv.boolean,
    }
)


ATTR_LONG_PRESS = "long_press"

ACTION_SCHEMA = cv.DEVICE_ACTION_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(NEO_APP_COMMANDS.keys()),
        vol.Required(ATTR_LONG_PRESS, default=False): cv.boolean,
    }
)


async def async_validate_action_config(
    hass: HomeAssistant, config: ConfigType
) -> ConfigType:
    """Validate config."""
    return async_validate_entity_schema(hass, config, ACTION_SCHEMA)


async def async_get_actions(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, Any]]:
    """List device actions for NEO Smartbox devices."""
    registry = dr.async_get(hass)
    device = registry.async_get(device_id)

    # A list of actions that can be performed on the device
    actions: list[dict[str, Any]] = []

    # Check if device belongs to this integration
    if device and any(
        entry_id
        for entry_id in device.config_entries
        if entry_id in hass.data.get(DOMAIN, {})
    ):
        # Add all actions for this device
        actions.extend(
            {
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_TYPE: action_type,
            }
            for action_type in NEO_APP_COMMANDS
        )

    return actions


async def async_get_action_capabilities(
    hass: HomeAssistant, config: ConfigType
) -> dict[str, vol.Schema]:
    """List action capabilities."""

    return {
        "extra_fields": vol.Schema(
            {
                vol.Required(ATTR_LONG_PRESS, default=False): cv.boolean,
            }
        )
    }


async def async_call_action_from_config(
    hass: HomeAssistant,
    config: ConfigType,
    variables: TemplateVarsType,
    context: Context | None,
) -> None:
    """Execute a device action."""

    service_data = {
        "device_id": [config[CONF_DEVICE_ID]],
        "action": config[CONF_TYPE],
        "long_press": config.get(CONF_LONG_PRESS, False),
    }

    await hass.services.async_call(
        DOMAIN,
        SERVICE_CUSTOM_ACTION,
        service_data,
        blocking=True,
        context=context,
    )


async def async_setup_entry(hass: HomeAssistant, config_entry) -> bool:
    """Set up device_action from a config entry."""
    # We don't need to register anything here
    # Home Assistant will automatically discover the device_action module
    return True
