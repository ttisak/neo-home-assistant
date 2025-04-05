# Create a new file: device_action.py
"""Provide device actions for Your Integration."""

from typing import Any

import voluptuous as vol

from homeassistant.components.device_automation import async_validate_entity_schema
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_TYPE
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.typing import ConfigType, TemplateVarsType

from .const import DOMAIN, NEO_APP_COMMANDS

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
    """List device actions for Your Integration devices."""
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
    action_type = config[CONF_TYPE]

    # Build service data
    service_data = {
        "device_id": config[CONF_DEVICE_ID],
        "action": action_type,
        "long_press": config[ATTR_LONG_PRESS],
    }

    # Call the service
    await hass.services.async_call(
        DOMAIN,
        "remote_key_action",
        service_data,
        blocking=True,
        context=context,
    )
