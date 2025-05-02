"""Data update coordinator for NEO Smartbox."""

from datetime import timedelta
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL
from .models import NeoSmartboxApiClient, NeoSmartboxDevice

_LOGGER = logging.getLogger(__name__)


class NeoSmartboxUpdateCoordinator(DataUpdateCoordinator[list[NeoSmartboxDevice]]):
    """Class to manage fetching NEO Smartbox data."""

    def __init__(self, hass: HomeAssistant, api_key: str) -> None:
        """Initialize data update coordinator."""
        self.hass = hass
        self.api_key = api_key
        self.api_client = self._create_api_client()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    def _create_api_client(self) -> NeoSmartboxApiClient:
        """Create a new API client instance."""
        return NeoSmartboxApiClient(
            api_key=self.api_key,
            session=async_get_clientsession(self.hass),
        )

    async def _async_update_data(self) -> list[NeoSmartboxDevice]:
        """Fetch data from API endpoint."""
        try:
            return await self.api_client.get_all_devices()
        except aiohttp.ClientConnectionError as err:
            _LOGGER.error("Connection error: %s", err)
            raise UpdateFailed(f"Connection error: {err}") from err
        except aiohttp.ClientError as err:
            if "Session is closed" in str(err):
                _LOGGER.warning("Session closed, recreating API client")
                self.api_client = self._create_api_client()
                return await self.api_client.get_all_devices()
            _LOGGER.error("Error communicating with API: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            _LOGGER.error("Error fetching neo_smartbox data: %s", err)
            raise UpdateFailed(f"Error fetching neo_smartbox data: {err}") from err
