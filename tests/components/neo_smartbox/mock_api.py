"""Mock API client for testing."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from homeassistant.components.neo_smartbox.models import NeoSmartboxApiClient

from .test_data import DEVICE_DATA


@pytest.fixture
def mock_api_client():
    """Return a mocked NEO Smartbox API client."""
    client = MagicMock(spec=NeoSmartboxApiClient)

    # Setup common methods
    client.get_all_devices = AsyncMock(return_value=DEVICE_DATA)
    client.send_key_action = AsyncMock(return_value=True)
    client.navigate_action = AsyncMock(return_value=True)

    return client
