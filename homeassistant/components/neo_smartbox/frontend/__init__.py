"""Frontend for NEO Smartbox integration."""

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

LOVELACE_DOMAIN = "lovelace"

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

    # Register the dashboard resource if Lovelace is in storage mode
    resource_url = "/static/neo_smartbox-card.js"

    if LOVELACE_DOMAIN in hass.data and hasattr(
        hass.data[LOVELACE_DOMAIN], "resources"
    ):
        resources = hass.data[LOVELACE_DOMAIN].resources
        if hasattr(resources, "async_create_item"):
            # Only attempt to register if we're in storage mode
            try:
                # Check if resource already exists to avoid duplicates
                if not resources.loaded:
                    await resources.async_load()
                    resources.loaded = True

                existing_items = resources.async_items()
                resource_exists = any(
                    item["url"] == resource_url for item in existing_items
                )

                if not resource_exists:
                    await resources.async_create_item(
                        {
                            "res_type": "module",
                            "url": resource_url,
                        }
                    )
                    _LOGGER.info(
                        "NEO Smartbox card automatically registered as a Lovelace resource"
                    )
            except (ValueError, RuntimeError) as ex:
                _LOGGER.warning("Unable to register card automatically: %s", ex)

    # We still log instructions for YAML mode users
    _LOGGER.info(
        "NEO Smartbox remote card registered at: %s\n"
        "If using YAML mode, add this to your lovelace resources:\n"
        "  - url: %s\n"
        "    type: module",
        resource_url,
        resource_url,
    )

    return True
