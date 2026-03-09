"""Tests for the WattWächter Plus integration setup."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from custom_components.wattwaechter.api import WattwaechterConnectionError
from custom_components.wattwaechter.coordinator import WattwaechterCoordinator

from .conftest import MOCK_ALIVE_RESPONSE, MOCK_METER_DATA, MOCK_SYSTEM_INFO


async def test_setup_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test successful integration setup."""
    with patch(
        "custom_components.wattwaechter.WattwaechterApiClient"
    ) as mock_cls:
        client = mock_cls.return_value
        client.async_alive = AsyncMock(return_value=MOCK_ALIVE_RESPONSE)
        client.async_get_meter_data = AsyncMock(return_value=MOCK_METER_DATA)
        client.async_get_system_info = AsyncMock(return_value=MOCK_SYSTEM_INFO)
        client.async_check_ota = AsyncMock(
            return_value={"ok": True, "data": {"update_available": False}}
        )
        client.host = "192.168.1.100"

        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert isinstance(mock_config_entry.runtime_data, WattwaechterCoordinator)
    assert mock_config_entry.runtime_data.mdns_name == "wattwaechter-aabbccddeeff.local"


async def test_setup_entry_connection_error(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test setup when device is unreachable."""
    with patch(
        "custom_components.wattwaechter.WattwaechterApiClient"
    ) as mock_cls:
        client = mock_cls.return_value
        client.async_alive = AsyncMock(
            side_effect=WattwaechterConnectionError("Connection refused")
        )

        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_unload_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test successful integration unload."""
    with patch(
        "custom_components.wattwaechter.WattwaechterApiClient"
    ) as mock_cls:
        client = mock_cls.return_value
        client.async_alive = AsyncMock(return_value=MOCK_ALIVE_RESPONSE)
        client.async_get_meter_data = AsyncMock(return_value=MOCK_METER_DATA)
        client.async_get_system_info = AsyncMock(return_value=MOCK_SYSTEM_INFO)
        client.async_check_ota = AsyncMock(
            return_value={"ok": True, "data": {"update_available": False}}
        )
        client.host = "192.168.1.100"

        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state is ConfigEntryState.LOADED

        await hass.config_entries.async_unload(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
