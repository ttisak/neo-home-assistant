"""Frontend for NEO Smartbox integration."""

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)
DOMAIN = "neo_smartbox"


async def async_setup(hass: HomeAssistant) -> bool:
    """Set up the NEO Smartbox frontend."""
    # Register the static path for our card
    frontend_path = Path(__file__).parent
    card_path = frontend_path / "card"

    # Register static files with the async method
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                url_path="/static/neo_smartbox-card.js",
                path=str(card_path / "neo-smartbox-remote-card.js"),
                cache_headers=False,
            )
        ]
    )

    # We'll log instructions for both YAML and storage modes
    _LOGGER.info(
        "NEO Smartbox remote card registered at: /static/neo_smartbox-card.js\n"
        "If using YAML mode, add this to your lovelace resources:\n"
        "  - url: /static/neo_smartbox-card.js\n"
        "    type: module"
    )

    return True
