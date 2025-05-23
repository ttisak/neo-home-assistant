"""Fixtures for NEO Smartbox integration tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.components.neo_smartbox.const import DOMAIN
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from .test_data import API_KEY, DEVICE_DATA

from tests.common import MockConfigEntry


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return the default mocked config entry."""
    return MockConfigEntry(
        title="NEO Smartbox",
        domain=DOMAIN,
        data={CONF_API_KEY: API_KEY},
        unique_id=API_KEY,
    )


@pytest.fixture
def mock_setup_entry() -> Generator[None]:
    """Mock setting up a config entry."""
    with patch(
        "homeassistant.components.neo_smartbox.async_setup_entry", return_value=True
    ):
        yield


@pytest.fixture
def mock_api_client() -> MagicMock:
    """Return a mocked NEO Smartbox API client."""
    client = MagicMock()
    client.get_all_devices = AsyncMock(return_value=DEVICE_DATA)
    client.send_key_action = AsyncMock(return_value=True)
    client.navigate_action = AsyncMock(return_value=True)
    return client


@pytest.fixture
def ignore_translations() -> list[str]:
    """Fixture to ignore translation for domain."""
    return [DOMAIN]


@pytest.fixture
async def init_integration(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, mock_api_client: MagicMock
) -> MockConfigEntry:
    """Set up the NEO Smartbox integration for testing."""
    mock_config_entry.add_to_hass(hass)

    with patch(
        "homeassistant.components.neo_smartbox.coordinator.NeoSmartboxApiClient",
        return_value=mock_api_client,
    ):
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    return mock_config_entry
