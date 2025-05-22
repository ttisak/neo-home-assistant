"""API client for NEO Smartbox."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import logging

import aiohttp

from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import (
    API_DEVICE_LIST,
    API_GET_SMART_TV_LIST,
    API_NAVIGATE_ACTION,
    API_SEND_KEY_ACTION,
    API_ZAP_LIST,
)

_LOGGER = logging.getLogger(__name__)


class NeoDeviceType(Enum):
    """Device types."""

    STB = "dt_stb"
    SMART_TV = "dt_tv"


@dataclass
class NeoSmartboxDevice:
    """NEO Smartbox device representation."""

    id: str
    name: str
    type: NeoDeviceType


@dataclass
class TvChannel:
    """TV channel representation."""

    id: str
    title: str
    number: str
    logo: str
    favorite: bool
    group: str


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
            "origin": "https://neo.io",
            "referer": "https://neo.io",
            "user-agent": "HomeAssistant/NEOSmartboxIntegration",
            "x-layout-id": "si_titan_flutter&platform=web",
        }

    async def get_all_devices(self) -> list[NeoSmartboxDevice]:
        """Get all devices."""

        stbs = await self._get_stb_list()
        smart_tvs = await self._get_smart_tv_list()

        return stbs + smart_tvs

    async def _get_stb_list(self) -> list[NeoSmartboxDevice]:
        """Get all STB devices."""
        try:
            stbResponse = await self.session.post(
                API_DEVICE_LIST,
                headers=self.headers,
                json={},
            )

            if stbResponse.status == 403:
                _LOGGER.error("Authentication error when getting devices")
                raise ConfigEntryAuthFailed("Invalid API key")

            stbResponse.raise_for_status()
            data = await stbResponse.json()

            return [
                NeoSmartboxDevice(
                    id=item["device_id"],
                    name=item["name"],
                    type=NeoDeviceType.STB,
                )
                for item in data.get("items", [])
            ]

        except aiohttp.ClientResponseError as err:
            if err.status == 403:
                _LOGGER.error("Authentication error when getting devices")
                raise ConfigEntryAuthFailed("Invalid API key") from err
            _LOGGER.error("Error getting devices: %s", err)
            raise

    async def _get_smart_tv_list(self) -> list[NeoSmartboxDevice]:
        """Get all Smart TVs."""
        try:
            response = await self.session.get(
                API_GET_SMART_TV_LIST,
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
                    id=item["uuid"],
                    name=item["device_name"],
                    type=NeoDeviceType.SMART_TV,
                )
                for item in data.get("devices", [])
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

    async def navigate_action(self, device_id: str, action: str) -> bool:
        """Send navigate action to device."""
        try:
            payload = {
                "device_id": device_id,
                "navigate_path": action,
            }

            _LOGGER.info("Sending command: %s", payload)

            response = await self.session.post(
                API_NAVIGATE_ACTION,
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

    async def get_channel_list(self) -> list[TvChannel]:
        """Get channel list."""
        try:
            response = await self.session.get(
                API_ZAP_LIST,
                headers=self.headers,
                json={},
            )

            if response.status == 403:
                _LOGGER.error("Authentication error when getting channel list")
                raise ConfigEntryAuthFailed("Invalid API key")

            response.raise_for_status()
            data = await response.json()

            return [
                TvChannel(
                    id=item["channel"]["id"],
                    title=item["channel"]["title"],
                    number=item["channel"]["number"],
                    logo=item["channel"]["logo"],
                    favorite=item["channel"]["favorite"],
                    group=item["channel"]["group"],
                )
                for item in data.get("data", [])
            ]

        except aiohttp.ClientResponseError as err:
            if err.status == 403:
                _LOGGER.error("Authentication error when getting channel list")
                raise ConfigEntryAuthFailed("Invalid API key") from err
            _LOGGER.error("Error getting channel list: %s", err)
            raise
