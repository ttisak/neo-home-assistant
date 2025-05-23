"""Tests for the NEO Smartbox coordinator."""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from homeassistant.components.neo_smartbox.const import UPDATE_INTERVAL
from homeassistant.components.neo_smartbox.coordinator import (
    NeoSmartboxUpdateCoordinator,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from .test_data import API_KEY, DEVICE_DATA


async def test_coordinator_update(hass: HomeAssistant) -> None:
    """Test coordinator update."""
    mock_api_client = MagicMock()
    mock_api_client.get_all_devices = AsyncMock(return_value=DEVICE_DATA)

    with patch(
        "homeassistant.components.neo_smartbox.coordinator.NeoSmartboxApiClient",
        return_value=mock_api_client,
    ):
        coordinator = NeoSmartboxUpdateCoordinator(hass, API_KEY)
        await coordinator.async_refresh()
        assert coordinator.data == DEVICE_DATA

    assert coordinator.data == DEVICE_DATA
    mock_api_client.get_all_devices.assert_called_once()


async def test_coordinator_connection_error(hass: HomeAssistant) -> None:
    """Test coordinator with connection error."""
    with patch(
        "homeassistant.components.neo_smartbox.coordinator.NeoSmartboxApiClient",
        autospec=True,
    ) as api_client_mock:
        client = api_client_mock.return_value
        client.get_all_devices = AsyncMock(
            side_effect=aiohttp.ClientConnectionError("Connection error")
        )

        coordinator = NeoSmartboxUpdateCoordinator(hass, API_KEY)
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


async def test_coordinator_client_error(hass: HomeAssistant) -> None:
    """Test coordinator with client error."""
    with patch(
        "homeassistant.components.neo_smartbox.coordinator.NeoSmartboxApiClient",
        autospec=True,
    ) as api_client_mock:
        client = api_client_mock.return_value
        client.get_all_devices = AsyncMock(
            side_effect=aiohttp.ClientError("Session is closed")
        )

        # Second attempt should work
        client2 = MagicMock()
        # Create a new mock for the recreated client that doesn't raise an error
        api_client_mock.return_value = client2
        client2.get_all_devices = AsyncMock(return_value=DEVICE_DATA)

        coordinator = NeoSmartboxUpdateCoordinator(hass, API_KEY)
        result = await coordinator._async_update_data()
        assert result == DEVICE_DATA


async def test_coordinator_update_interval(hass: HomeAssistant) -> None:
    """Test coordinator update interval."""
    with patch(
        "homeassistant.components.neo_smartbox.coordinator.NeoSmartboxApiClient",
    ):
        coordinator = NeoSmartboxUpdateCoordinator(hass, API_KEY)

    assert coordinator.update_interval == timedelta(seconds=UPDATE_INTERVAL)
