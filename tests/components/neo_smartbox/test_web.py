"""Tests for the NEO Smartbox web component."""

from unittest.mock import patch

from homeassistant.components.neo_smartbox.web import async_setup
from homeassistant.core import HomeAssistant


async def test_async_setup(hass: HomeAssistant) -> None:
    """Test that the web view is correctly set up."""
    with patch("homeassistant.components.neo_smartbox.web._LOGGER") as mock_logger:
        result = await async_setup(hass)
        assert result is True
        mock_logger.debug.assert_called_once_with(
            "Setting up NEO Smartbox web resources"
        )
