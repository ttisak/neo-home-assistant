"""Config flow for NEO Smartbox integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .models import NeoSmartboxApiClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_API_KEY): str})


class NeoSmartboxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NEO Smartbox."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                devices = await self._validate_api_key(user_input[CONF_API_KEY])

                if not devices:
                    errors["base"] = "no_devices_found"
                else:
                    await self.async_set_unique_id(user_input[CONF_API_KEY])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title="NEO Smartbox",
                        data={CONF_API_KEY: user_input[CONF_API_KEY]},
                    )
            except aiohttp.ClientResponseError as err:
                if err.status == 403:
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "unknown"
                    _LOGGER.error("Connection error: %s", err)
            except aiohttp.ClientConnectionError:
                errors["base"] = "unknown"
                _LOGGER.error("Connection error")
            except ConfigEntryAuthFailed:
                errors["base"] = "invalid_auth"
            except Exception as err:
                _LOGGER.exception("Unexpected exception", exc_info=err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def _validate_api_key(self, api_key: str) -> list:
        """Validate the API key by retrieving devices."""
        session = async_get_clientsession(self.hass)
        api_client = NeoSmartboxApiClient(api_key, session)
        return await api_client.get_all_devices()
