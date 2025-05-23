"""Tests for the NEO Smartbox API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from homeassistant.components.neo_smartbox.const import (
    API_DEVICE_LIST,
    API_GET_SMART_TV_LIST,
    API_NAVIGATE_ACTION,
    API_SEND_KEY_ACTION,
    API_ZAP_LIST,
)
from homeassistant.components.neo_smartbox.models import (
    NeoDeviceType,
    NeoSmartboxApiClient,
    NeoSmartboxDevice,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .test_data import API_KEY, STB_DEVICE_ID


@pytest.fixture
def mock_session():
    """Return a mocked aiohttp ClientSession."""
    return MagicMock(spec=aiohttp.ClientSession)


async def test_get_all_devices(
    mock_api_client: AsyncMock,
) -> None:
    """Test getting all devices."""

    with patch(
        "homeassistant.components.neo_smartbox.coordinator.NeoSmartboxApiClient",
        return_value=mock_api_client,
    ):
        # Setup mock responses
        stb_response = MagicMock()
        stb_response.status = 200
        stb_response.json = AsyncMock(
            return_value={
                "items": [
                    {"device_id": "stb1", "name": "Living Room STB"},
                    {"device_id": "stb2", "name": "Bedroom STB"},
                ]
            }
        )

        tv_response = MagicMock()
        tv_response.status = 200
        tv_response.json = AsyncMock(
            return_value={
                "devices": [
                    {"uuid": "tv1", "device_name": "Living Room TV"},
                ]
            }
        )

        # Mock the post method
        mock_session.post = AsyncMock(return_value=stb_response)
        # Mock the get method for smart TVs
        mock_session.get = AsyncMock(return_value=tv_response)

        # Create client and call method
        client = NeoSmartboxApiClient(API_KEY, mock_session)
        devices = await client.get_all_devices()

        # Verify results
        assert len(devices) == 3
        assert isinstance(devices[0], NeoSmartboxDevice)
        assert devices[0].id == "stb1"
        assert devices[0].name == "Living Room STB"
        assert devices[0].type == NeoDeviceType.STB

        assert devices[2].id == "tv1"
        assert devices[2].name == "Living Room TV"
        assert devices[2].type == NeoDeviceType.SMART_TV

        # Verify API calls - use post for device list
        mock_session.post.assert_called_with(
            API_DEVICE_LIST, headers=client.headers, json={}
        )
        mock_session.get.assert_any_call(
            API_GET_SMART_TV_LIST, headers=client.headers, json={}
        )


async def test_get_stb_list_auth_error(mock_session: MagicMock) -> None:
    """Test authentication error when getting STB list."""
    stb_response = MagicMock()
    stb_response.status = 403

    mock_session.post = AsyncMock(return_value=stb_response)

    client = NeoSmartboxApiClient(API_KEY, mock_session)

    with pytest.raises(ConfigEntryAuthFailed, match="Invalid API key"):
        await client._get_stb_list()


async def test_send_key_action(mock_session: MagicMock) -> None:
    """Test sending key action."""
    response = MagicMock()
    response.status = 200
    response.json = AsyncMock(return_value={"success": True})

    mock_session.post = AsyncMock(return_value=response)

    client = NeoSmartboxApiClient(API_KEY, mock_session)
    result = await client.send_key_action(
        STB_DEVICE_ID, "Home", key_repeat=0, long_press=False
    )

    assert result is True
    mock_session.post.assert_called_once_with(
        API_SEND_KEY_ACTION,
        headers=client.headers,
        json={
            "device_id": STB_DEVICE_ID,
            "key_name": "Home",
            "key_repeat": 0,
            "long_press": False,
        },
    )


async def test_navigate_action_tune(mock_session: MagicMock) -> None:
    """Test navigating to a live channel using navigate_action."""
    response = MagicMock()
    response.status = 200
    response.json = AsyncMock(return_value={"success": True})

    mock_session.post = AsyncMock(return_value=response)

    client = NeoSmartboxApiClient(API_KEY, mock_session)
    result = await client.navigate_action(STB_DEVICE_ID, "tune/channel123")

    assert result is True
    mock_session.post.assert_called_once_with(
        API_NAVIGATE_ACTION,
        headers=client.headers,
        json={
            "device_id": STB_DEVICE_ID,
            "navigate_path": "tune/channel123",
        },
    )


async def test_navigate_action_custom(mock_session: MagicMock) -> None:
    """Test navigating to a custom action."""
    response = MagicMock()
    response.status = 200
    response.json = AsyncMock(return_value={"success": True})

    mock_session.post = AsyncMock(return_value=response)

    client = NeoSmartboxApiClient(API_KEY, mock_session)
    result = await client.navigate_action(STB_DEVICE_ID, "some_action")

    assert result is True
    mock_session.post.assert_called_once_with(
        API_NAVIGATE_ACTION,
        headers=client.headers,
        json={
            "device_id": STB_DEVICE_ID,
            "navigate_path": "some_action",
        },
    )


async def test_get_channel_list(mock_session: MagicMock) -> None:
    """Test getting channel list."""
    response = MagicMock()
    response.status = 200
    response.json = AsyncMock(
        return_value={
            "data": [
                {
                    "channel": {
                        "id": "ch1",
                        "title": "Channel 1",
                        "number": "1",
                        "logo": "logo1.png",
                        "favorite": True,
                        "group": "Group 1",
                    }
                }
            ]
        }
    )

    mock_session.get = AsyncMock(return_value=response)

    client = NeoSmartboxApiClient(API_KEY, mock_session)
    channels = await client.get_channel_list()

    assert len(channels) == 1
    assert channels[0].id == "ch1"
    assert channels[0].title == "Channel 1"
    assert channels[0].number == "1"
    assert channels[0].logo == "logo1.png"
    assert channels[0].favorite is True
    assert channels[0].group == "Group 1"

    mock_session.get.assert_called_once_with(
        API_ZAP_LIST,
        headers=client.headers,
        json={},
    )
