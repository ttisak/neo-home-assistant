"""Data update coordinator for NEO Smartbox."""

from datetime import timedelta
import logging

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
        self.api_client = NeoSmartboxApiClient(
            api_key=api_key,
            session=async_get_clientsession(hass),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> list[NeoSmartboxDevice]:
        """Fetch data from API endpoint."""
        try:
            return await self.api_client.get_devices()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
