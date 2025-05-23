"""Tests for the NEO Smartbox initialization."""

from unittest.mock import AsyncMock, patch

from homeassistant.components.neo_smartbox.const import DOMAIN
from homeassistant.components.remote import DOMAIN as REMOTE_DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from tests.common import MockConfigEntry


async def test_setup_component(hass: HomeAssistant) -> None:
    """Test setting up the NEO Smartbox component."""
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()
    assert DOMAIN in hass.data


async def test_setup_config_entry(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_api_client: AsyncMock
) -> None:
    """Test setting up the config entry."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.neo_smartbox.coordinator.NeoSmartboxApiClient",
        return_value=mock_api_client,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert DOMAIN in hass.data
    assert mock_config_entry.entry_id in hass.data[DOMAIN]
    assert len(hass.states.async_entity_ids(REMOTE_DOMAIN)) == 2  # Two mock devices


async def test_unload_config_entry(
    hass: HomeAssistant, init_integration: MockConfigEntry, mock_api_client: AsyncMock
) -> None:
    """Test unloading the config entry."""
    assert await hass.config_entries.async_unload(init_integration.entry_id)
    await hass.async_block_till_done()

    assert init_integration.state is ConfigEntryState.NOT_LOADED
    assert DOMAIN in hass.data
    assert init_integration.entry_id not in hass.data[DOMAIN]


async def test_setup_config_entry_connection_error(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test setup with connection error."""
    with patch(
        "homeassistant.components.neo_smartbox.coordinator.NeoSmartboxApiClient",
        autospec=True,
    ) as api_client_mock:
        client = api_client_mock.return_value
        client.get_all_devices = AsyncMock(
            side_effect=ConnectionError("Connection error")
        )

        mock_config_entry.add_to_hass(hass)
        assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
