"""API client for NEO Smartbox."""

from __future__ import annotations

from dataclasses import dataclass
import logging

import aiohttp

from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import API_DEVICE_LIST, API_SEND_KEY_ACTION

_LOGGER = logging.getLogger(__name__)


@dataclass
class NeoSmartboxDevice:
    """NEO Smartbox device representation."""

    name: str
    device_id: str
    is_available: bool
    oblo_id: str | None
    oblo_secure_id: str | None


class NeoSmartboxApiClient:
    """API client for NEO Smartbox."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self.api_key = api_key
        self.session = session
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9,sl;q=0.8",
            "authorization": f"APIGW-AUTH-TOK {api_key}",
            "content-type": "application/json",
            "origin": "https://www.neo.io",
            "referer": "https://www.neo.io/",
            "user-agent": "HomeAssistant/NEOSmartboxIntegration",
            "x-layout-id": "si_titan_flutter&platform=web",
        }

    async def get_devices(self) -> list[NeoSmartboxDevice]:
        """Get all available devices."""
        try:
            response = await self.session.post(
                API_DEVICE_LIST,
                headers=self.headers,
                json={},
            )

            if response.status == 403:
                _LOGGER.error("Authentication error when getting devices")
                raise ConfigEntryAuthFailed("Invalid API key")

            response.raise_for_status()
            data = await response.json()

            return [
                NeoSmartboxDevice(
                    name=item["name"],
                    device_id=item["device_id"],
                    is_available=item["is_available"],
                    oblo_id=item.get("oblo_id", ""),
                    oblo_secure_id=item.get("oblo_secure_id", ""),
                )
                for item in data.get("items", [])
            ]

        except aiohttp.ClientResponseError as err:
            if err.status == 403:
                _LOGGER.error("Authentication error when getting devices")
                raise ConfigEntryAuthFailed("Invalid API key") from err
            _LOGGER.error("Error getting devices: %s", err)
            raise

    async def send_key_action(
        self,
        device_id: str,
        key_name: str,
        long_press: bool = False,
        key_repeat: int = 0,
    ) -> bool:
        """Send key action to device."""
        try:
            payload = {
                "device_id": device_id,
                "key_name": key_name,
                "key_repeat": key_repeat,
                "long_press": long_press,
            }

            _LOGGER.info("Sending command: %s", payload)

            response = await self.session.post(
                API_SEND_KEY_ACTION,
                headers=self.headers,
                json=payload,
            )

            if response.status == 403:
                _LOGGER.error("Authentication error when sending command")
                raise ConfigEntryAuthFailed("Invalid API key")

            response.raise_for_status()
        except aiohttp.ClientResponseError as err:
            if err.status == 403:
                _LOGGER.debug("Authentication error when sending command")
                raise ConfigEntryAuthFailed("Invalid API key") from err
            _LOGGER.debug("Error sending command: %s", err)
            return False
        else:
            return True
