"""Tests for the NEO Smartbox config flow."""

from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from homeassistant.components.neo_smartbox.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .test_data import API_KEY

pytestmark = pytest.mark.usefixtures("mock_setup_entry")


async def test_user_flow(hass: HomeAssistant, mock_api_client: AsyncMock) -> None:
    """Test the user initiated config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}

    with patch(
        "homeassistant.components.neo_smartbox.config_flow.NeoSmartboxApiClient",
        return_value=mock_api_client,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_API_KEY: API_KEY}
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "NEO Smartbox"
    assert result["data"] == {CONF_API_KEY: API_KEY}


async def test_user_flow_no_devices(hass: HomeAssistant) -> None:
    """Test the user initiated config flow with no devices found."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "homeassistant.components.neo_smartbox.config_flow.NeoSmartboxApiClient",
        autospec=True,
    ) as api_client_mock:
        client = api_client_mock.return_value
        client.get_all_devices = AsyncMock(return_value=[])
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_API_KEY: API_KEY}
        )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "no_devices_found"}


async def test_user_flow_auth_error(hass: HomeAssistant) -> None:
    """Test the user initiated config flow with authentication error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "homeassistant.components.neo_smartbox.config_flow.NeoSmartboxApiClient",
        autospec=True,
    ) as api_client_mock:
        client = api_client_mock.return_value
        client.get_all_devices = AsyncMock(
            side_effect=aiohttp.ClientResponseError(
                request_info=None, history=None, status=403
            )
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_API_KEY: API_KEY}
        )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "invalid_auth"}


async def test_user_flow_connection_error(hass: HomeAssistant) -> None:
    """Test the user initiated config flow with connection error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "homeassistant.components.neo_smartbox.config_flow.NeoSmartboxApiClient",
        autospec=True,
    ) as api_client_mock:
        client = api_client_mock.return_value
        client.get_all_devices = AsyncMock(side_effect=aiohttp.ClientConnectionError())
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_API_KEY: API_KEY}
        )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "unknown"}


async def test_user_flow_unknown_error(hass: HomeAssistant) -> None:
    """Test the user initiated config flow with unknown error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "homeassistant.components.neo_smartbox.config_flow.NeoSmartboxApiClient",
        autospec=True,
    ) as api_client_mock:
        client = api_client_mock.return_value
        client.get_all_devices = AsyncMock(side_effect=Exception("Unknown error"))
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_API_KEY: API_KEY}
        )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "unknown"}
