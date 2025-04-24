"""Web resources for NEO Smartbox integration."""

import logging
from typing import Final

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)
DOMAIN: Final = "neo_smartbox"


async def async_setup(hass: HomeAssistant) -> bool:
    """Set up web resources for NEO Smartbox."""
    _LOGGER.debug("Setting up NEO Smartbox web resources")
    return True
