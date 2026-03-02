"""Tests for the WattWächter Plus config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.wattwaechter.api import (
    WattwaechterAuthError,
    WattwaechterConnectionError,
)
from custom_components.wattwaechter.const import CONF_DEVICE_ID, DOMAIN

from .conftest import (
    MOCK_ALIVE_RESPONSE,
    MOCK_CONFIG_DATA,
    MOCK_DEVICE_ID,
    MOCK_HOST,
    MOCK_SYSTEM_INFO,
    MOCK_TOKEN,
)


@pytest.fixture(autouse=True)
def mock_setup_entry():
    """Mock the integration setup to avoid full platform loading."""
    with patch(
        "custom_components.wattwaechter.async_setup_entry",
        return_value=True,
    ) as mock:
        yield mock


# --- User Flow (manual configuration) ---


async def test_user_flow_success(hass: HomeAssistant) -> None:
    """Test successful manual configuration."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "custom_components.wattwaechter.config_flow.WattwaechterApiClient"
    ) as mock_cls:
        client = mock_cls.return_value
        client.async_alive = AsyncMock(return_value=MOCK_ALIVE_RESPONSE)
        client.async_get_system_info = AsyncMock(return_value=MOCK_SYSTEM_INFO)

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: MOCK_HOST, CONF_TOKEN: MOCK_TOKEN},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"WattWächter {MOCK_DEVICE_ID}"
    assert result["data"][CONF_HOST] == MOCK_HOST
    assert result["data"][CONF_TOKEN] == MOCK_TOKEN
    assert result["data"][CONF_DEVICE_ID] == MOCK_DEVICE_ID


async def test_user_flow_no_token(hass: HomeAssistant) -> None:
    """Test manual configuration without API token."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.wattwaechter.config_flow.WattwaechterApiClient"
    ) as mock_cls:
        client = mock_cls.return_value
        client.async_alive = AsyncMock(return_value=MOCK_ALIVE_RESPONSE)
        client.async_get_system_info = AsyncMock(return_value=MOCK_SYSTEM_INFO)

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: MOCK_HOST},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_TOKEN] is None


async def test_user_flow_cannot_connect(hass: HomeAssistant) -> None:
    """Test manual configuration with connection error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.wattwaechter.config_flow.WattwaechterApiClient"
    ) as mock_cls:
        client = mock_cls.return_value
        client.async_alive = AsyncMock(
            side_effect=WattwaechterConnectionError("Connection refused")
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: MOCK_HOST},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"


async def test_user_flow_invalid_auth(hass: HomeAssistant) -> None:
    """Test manual configuration with invalid token."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.wattwaechter.config_flow.WattwaechterApiClient"
    ) as mock_cls:
        client = mock_cls.return_value
        client.async_alive = AsyncMock(return_value=MOCK_ALIVE_RESPONSE)
        client.async_get_system_info = AsyncMock(
            side_effect=WattwaechterAuthError("Invalid token")
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: MOCK_HOST, CONF_TOKEN: "bad-token"},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_auth"


# --- Reauth Flow ---


async def test_reauth_flow_success(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test successful reauthentication with new token."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": mock_config_entry.entry_id,
        },
        data=mock_config_entry.data,
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    with patch(
        "custom_components.wattwaechter.config_flow.WattwaechterApiClient"
    ) as mock_cls:
        client = mock_cls.return_value
        client.async_get_system_info = AsyncMock(return_value=MOCK_SYSTEM_INFO)

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_TOKEN: "new-valid-token"},
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert mock_config_entry.data[CONF_TOKEN] == "new-valid-token"


async def test_reauth_flow_invalid_token(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test reauthentication with invalid token."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": mock_config_entry.entry_id,
        },
        data=mock_config_entry.data,
    )

    with patch(
        "custom_components.wattwaechter.config_flow.WattwaechterApiClient"
    ) as mock_cls:
        client = mock_cls.return_value
        client.async_get_system_info = AsyncMock(
            side_effect=WattwaechterAuthError("Invalid token")
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_TOKEN: "bad-token"},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_auth"


async def test_reauth_flow_cannot_connect(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test reauthentication when device is unreachable."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": mock_config_entry.entry_id,
        },
        data=mock_config_entry.data,
    )

    with patch(
        "custom_components.wattwaechter.config_flow.WattwaechterApiClient"
    ) as mock_cls:
        client = mock_cls.return_value
        client.async_get_system_info = AsyncMock(
            side_effect=WattwaechterConnectionError("Connection refused")
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_TOKEN: MOCK_TOKEN},
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"


# --- Options Flow ---


async def test_options_flow(hass: HomeAssistant, mock_config_entry) -> None:
    """Test options flow for scan interval."""
    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"scan_interval": 60},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["scan_interval"] == 60
