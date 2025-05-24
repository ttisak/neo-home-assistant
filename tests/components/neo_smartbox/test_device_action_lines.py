"""Tests for coverage gaps in device_action.py."""

from unittest.mock import patch

from homeassistant.components.neo_smartbox import (
    DOMAIN,
    NAVIGATE_TO_CUSTOM_ACTION,
    REMOTE_KEY_ACTION,
)
from homeassistant.components.neo_smartbox.device_action import (
    ATTR_CHANNEL_ID,
    ATTR_DESTINATION,
    ATTR_LONG_PRESS,
    NAVIGATE_TO,
    NAVIGATE_TO_LIVE_CHANNEL,
    async_call_action_from_config,
)
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_TYPE
from homeassistant.core import HomeAssistant

from tests.common import async_mock_service


async def test_call_remote_key(hass: HomeAssistant) -> None:
    """Test calling remote key action from config."""
    config = {
        CONF_DEVICE_ID: "device-id",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: "Home",
        ATTR_LONG_PRESS: False,
    }

    calls = async_mock_service(hass, DOMAIN, REMOTE_KEY_ACTION)
    await async_call_action_from_config(hass, config, {}, None)

    # Verify the service was called with correct parameters
    assert len(calls) == 1
    call = calls[0]
    assert call.domain == DOMAIN
    assert call.service == REMOTE_KEY_ACTION
    assert call.data["device_id"] == ["device-id"]
    assert call.data["action"] == "Home"
    assert call.data["long_press"] is False


async def test_navigate_to(hass: HomeAssistant) -> None:
    """Test calling navigate_to action from config."""
    config = {
        CONF_DEVICE_ID: "device-id",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: NAVIGATE_TO,
        ATTR_DESTINATION: "app://settings",
    }

    calls = async_mock_service(hass, DOMAIN, NAVIGATE_TO_CUSTOM_ACTION)
    await async_call_action_from_config(hass, config, {}, None)

    # Verify the service was called with correct parameters
    assert len(calls) == 1
    call = calls[0]
    assert call.domain == DOMAIN
    assert call.service == NAVIGATE_TO_CUSTOM_ACTION
    assert call.data["device_id"] == ["device-id"]
    assert call.data["action"] == "app://settings"


async def test_navigate_to_live_channel(hass: HomeAssistant) -> None:
    """Test calling navigate_to_live_channel action from config."""
    config = {
        CONF_DEVICE_ID: "device-id",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: NAVIGATE_TO_LIVE_CHANNEL,
        ATTR_CHANNEL_ID: "ch1",
    }

    calls = async_mock_service(hass, DOMAIN, NAVIGATE_TO_CUSTOM_ACTION)
    await async_call_action_from_config(hass, config, {}, None)

    # Verify the service was called with correct parameters
    assert len(calls) == 1
    call = calls[0]
    assert call.domain == DOMAIN
    assert call.service == NAVIGATE_TO_CUSTOM_ACTION
    assert call.data["device_id"] == ["device-id"]
    assert call.data["action"] == "app://player/livetv/id/ch1"


async def test_navigate_to_missing_destination(hass: HomeAssistant) -> None:
    """Test error case when destination is missing."""
    config = {
        CONF_DEVICE_ID: "device-id",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: NAVIGATE_TO,
    }

    calls = async_mock_service(hass, DOMAIN, NAVIGATE_TO_CUSTOM_ACTION)

    with patch(
        "homeassistant.components.neo_smartbox.device_action._LOGGER.error"
    ) as mock_log:
        await async_call_action_from_config(hass, config, {}, None)

        # Should log an error
        mock_log.assert_called_once()
        assert "Invalid destination" in mock_log.call_args[0][0]

    # Should not call the service
    assert len(calls) == 0


async def test_navigate_to_live_channel_missing_channel(hass: HomeAssistant) -> None:
    """Test error case when channel ID is missing."""
    config = {
        CONF_DEVICE_ID: "device-id",
        CONF_DOMAIN: DOMAIN,
        CONF_TYPE: NAVIGATE_TO_LIVE_CHANNEL,
    }

    calls = async_mock_service(hass, DOMAIN, NAVIGATE_TO_CUSTOM_ACTION)

    with patch(
        "homeassistant.components.neo_smartbox.device_action._LOGGER.error"
    ) as mock_log:
        await async_call_action_from_config(hass, config, {}, None)

        # Should log an error
        mock_log.assert_called_once()
        assert "Channel ID is required" in mock_log.call_args[0][0]

    # Should not call the service
    assert len(calls) == 0
