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

from . import DOMAIN, NAVIGATE_TO_CUSTOM_ACTION, REMOTE_KEY_ACTION
from .const import NEO_APP_COMMANDS

_LOGGER = logging.getLogger(__name__)


CONF_LONG_PRESS = "long_press"

NAVIGATE_TO = "navigate_to"
NAVIGATE_TO_LIVE_CHANNEL = "navigate_to_live_channel"

ATTR_DESTINATION = "destination"
ATTR_CHANNEL_ID = "channel_id"
ATTR_LONG_PRESS = "long_press"


ACTION_TYPES = list(NEO_APP_COMMANDS.keys())
ACTION_TYPES.append(NAVIGATE_TO)
ACTION_TYPES.append(NAVIGATE_TO_LIVE_CHANNEL)


ACTION_SCHEMA = cv.DEVICE_ACTION_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_TYPE): vol.In(ACTION_TYPES),
        vol.Optional(ATTR_LONG_PRESS, default=False): cv.boolean,
        vol.Optional(ATTR_DESTINATION): cv.string,
        vol.Optional(ATTR_CHANNEL_ID): cv.string,
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
    actions: list[dict[str, Any]] = [
        {
            CONF_DEVICE_ID: device_id,
            CONF_DOMAIN: DOMAIN,
            CONF_TYPE: NAVIGATE_TO,
        },
        {
            CONF_DEVICE_ID: device_id,
            CONF_DOMAIN: DOMAIN,
            CONF_TYPE: NAVIGATE_TO_LIVE_CHANNEL,
        },
    ]

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

    if config[CONF_TYPE] == NAVIGATE_TO:
        return {
            "extra_fields": vol.Schema(
                {
                    vol.Required(ATTR_DESTINATION): cv.string,
                }
            )
        }

    if config[CONF_TYPE] == NAVIGATE_TO_LIVE_CHANNEL:
        # Get the list of channels from the coordinator

        # This is a placeholder. You should replace it with the actual logic to get the channels.

        device_registry = dr.async_get(hass)
        device = device_registry.async_get(config[CONF_DEVICE_ID])

        if not device:
            raise ValueError(f"Device not found: {config[CONF_DEVICE_ID]}")

        coordinator = hass.data[DOMAIN].get(
            next(
                (
                    entry_id
                    for entry_id in device.config_entries
                    if entry_id in hass.data[DOMAIN]
                ),
                None,
            )
        )

        if not coordinator:
            raise ValueError(
                f"Coordinator not found for device {config[CONF_DEVICE_ID]}"
            )

        tv_channels = await coordinator.api_client.get_channel_list()

        channel_options = {
            channel.id: f"{channel.number} - {channel.title}" for channel in tv_channels
        }

        return {
            "extra_fields": vol.Schema(
                {
                    vol.Required(ATTR_CHANNEL_ID): vol.In(channel_options),
                }
            )
        }

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

    if (
        config[CONF_TYPE] != NAVIGATE_TO
        and config[CONF_TYPE] != NAVIGATE_TO_LIVE_CHANNEL
    ):
        service_data = {
            "device_id": [config[CONF_DEVICE_ID]],
            "action": config[CONF_TYPE],
            "long_press": config.get(CONF_LONG_PRESS, False),
        }

        await hass.services.async_call(
            DOMAIN,
            REMOTE_KEY_ACTION,
            service_data,
            blocking=True,
            context=context,
        )

        return

    if config[CONF_TYPE] == NAVIGATE_TO:
        destination = config.get(ATTR_DESTINATION)
        if not destination:
            _LOGGER.error("Invalid destination: %s", destination)
            return

        navigate_to_path = destination

    elif config[CONF_TYPE] == NAVIGATE_TO_LIVE_CHANNEL:
        channel_id = config.get(ATTR_CHANNEL_ID)
        if not channel_id:
            _LOGGER.error("Channel ID is required for navigate_to_live_channel")
            return

        navigate_to_path = f"app://player/livetv/id/{channel_id}"

    service_data = {
        "device_id": [config[CONF_DEVICE_ID]],
        "action": navigate_to_path,
    }

    await hass.services.async_call(
        DOMAIN,
        NAVIGATE_TO_CUSTOM_ACTION,
        service_data,
        blocking=True,
        context=context,
    )


async def async_setup_entry(hass: HomeAssistant, config_entry) -> bool:
    """Set up device_action from a config entry."""
    # We don't need to register anything here
    # Home Assistant will automatically discover the device_action module
    return True
