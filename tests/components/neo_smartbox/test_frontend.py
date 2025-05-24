"""Tests for the NEO Smartbox frontend."""

from unittest.mock import AsyncMock, MagicMock

from homeassistant.components.lovelace import DOMAIN as LOVELACE_DOMAIN
from homeassistant.components.neo_smartbox.frontend import async_setup
from homeassistant.core import HomeAssistant


async def test_setup_with_lovelace_storage_mode(hass: HomeAssistant) -> None:
    """Test setup with Lovelace in storage mode."""
    # Mock the HTTP component
    mock_http = MagicMock()
    mock_http.async_register_static_paths = AsyncMock()
    hass.http = mock_http

    # Mock the resources object
    mock_resources = MagicMock()
    mock_resources.loaded = False
    mock_resources.async_load = AsyncMock()
    mock_resources.async_items = MagicMock(return_value=[])
    mock_resources.async_create_item = AsyncMock()

    # Mock the lovelace data structure
    hass.data[LOVELACE_DOMAIN] = MagicMock()
    hass.data[LOVELACE_DOMAIN].resources = mock_resources

    result = await async_setup(hass)

    assert result is True
    mock_http.async_register_static_paths.assert_called_once()
    mock_resources.async_load.assert_called_once()
    mock_resources.async_create_item.assert_called_once()


async def test_setup_with_lovelace_already_loaded(hass: HomeAssistant) -> None:
    """Test setup with Lovelace resources already loaded."""
    # Mock the HTTP component
    mock_http = MagicMock()
    mock_http.async_register_static_paths = AsyncMock()
    hass.http = mock_http

    # Mock the resources object
    mock_resources = MagicMock()
    mock_resources.loaded = True  # Already loaded
    mock_resources.async_load = AsyncMock()
    mock_resources.async_items = MagicMock(return_value=[])
    mock_resources.async_create_item = AsyncMock()

    # Mock the lovelace data structure
    hass.data[LOVELACE_DOMAIN] = MagicMock()
    hass.data[LOVELACE_DOMAIN].resources = mock_resources

    result = await async_setup(hass)

    assert result is True
    mock_http.async_register_static_paths.assert_called_once()
    mock_resources.async_load.assert_not_called()  # Should not load if already loaded
    mock_resources.async_create_item.assert_called_once()


async def test_setup_resource_already_exists(hass: HomeAssistant) -> None:
    """Test setup when resource already exists."""
    # Mock the HTTP component
    mock_http = MagicMock()
    mock_http.async_register_static_paths = AsyncMock()
    hass.http = mock_http

    # Mock the resources object with existing resource
    mock_resources = MagicMock()
    mock_resources.loaded = False
    mock_resources.async_load = AsyncMock()
    mock_resources.async_items = MagicMock(
        return_value=[{"url": "/static/neo_smartbox-card.js"}]
    )
    mock_resources.async_create_item = AsyncMock()

    # Mock the lovelace data structure
    hass.data[LOVELACE_DOMAIN] = MagicMock()
    hass.data[LOVELACE_DOMAIN].resources = mock_resources

    result = await async_setup(hass)

    assert result is True
    mock_http.async_register_static_paths.assert_called_once()
    mock_resources.async_load.assert_called_once()
    mock_resources.async_create_item.assert_not_called()  # Should not create if exists


async def test_setup_with_value_error(hass: HomeAssistant) -> None:
    """Test setup when ValueError is raised."""
    # Mock the HTTP component
    mock_http = MagicMock()
    mock_http.async_register_static_paths = AsyncMock()
    hass.http = mock_http

    # Mock the resources object that raises ValueError
    mock_resources = MagicMock()
    mock_resources.loaded = False
    mock_resources.async_load = AsyncMock(side_effect=ValueError("Test error"))

    # Mock the lovelace data structure
    hass.data[LOVELACE_DOMAIN] = MagicMock()
    hass.data[LOVELACE_DOMAIN].resources = mock_resources

    result = await async_setup(hass)

    assert result is True  # Should still return True even with error
    mock_http.async_register_static_paths.assert_called_once()


async def test_setup_with_runtime_error(hass: HomeAssistant) -> None:
    """Test setup when RuntimeError is raised."""
    # Mock the HTTP component
    mock_http = MagicMock()
    mock_http.async_register_static_paths = AsyncMock()
    hass.http = mock_http

    # Mock the resources object that raises RuntimeError
    mock_resources = MagicMock()
    mock_resources.loaded = False
    mock_resources.async_load = AsyncMock(side_effect=RuntimeError("Test error"))

    # Mock the lovelace data structure
    hass.data[LOVELACE_DOMAIN] = MagicMock()
    hass.data[LOVELACE_DOMAIN].resources = mock_resources

    result = await async_setup(hass)

    assert result is True  # Should still return True even with error
    mock_http.async_register_static_paths.assert_called_once()


async def test_setup_no_lovelace(hass: HomeAssistant) -> None:
    """Test setup when Lovelace is not available."""
    # Mock the HTTP component
    mock_http = MagicMock()
    mock_http.async_register_static_paths = AsyncMock()
    hass.http = mock_http

    # Don't add LOVELACE_DOMAIN to hass.data
    result = await async_setup(hass)

    assert result is True
    mock_http.async_register_static_paths.assert_called_once()


async def test_setup_no_resources_attribute(hass: HomeAssistant) -> None:
    """Test setup when Lovelace object has no resources attribute."""
    # Mock the HTTP component
    mock_http = MagicMock()
    mock_http.async_register_static_paths = AsyncMock()
    hass.http = mock_http

    # Mock the lovelace data structure without resources attribute
    hass.data[LOVELACE_DOMAIN] = MagicMock()
    delattr(hass.data[LOVELACE_DOMAIN], "resources")

    result = await async_setup(hass)

    assert result is True
    mock_http.async_register_static_paths.assert_called_once()


async def test_setup_no_async_create_item(hass: HomeAssistant) -> None:
    """Test setup when resources has no async_create_item method."""
    # Mock the HTTP component
    mock_http = MagicMock()
    mock_http.async_register_static_paths = AsyncMock()
    hass.http = mock_http

    # Mock the resources object without async_create_item
    mock_resources = MagicMock()
    delattr(mock_resources, "async_create_item")

    # Mock the lovelace data structure
    hass.data[LOVELACE_DOMAIN] = MagicMock()
    hass.data[LOVELACE_DOMAIN].resources = mock_resources

    result = await async_setup(hass)

    assert result is True
    mock_http.async_register_static_paths.assert_called_once()
