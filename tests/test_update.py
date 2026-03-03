"""Tests for the WattWächter Plus update platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.core import HomeAssistant

from custom_components.wattwaechter.api import (
    WattwaechterAuthError,
    WattwaechterConnectionError,
)

from .conftest import (
    MOCK_ALIVE_RESPONSE,
    MOCK_FW_VERSION,
    MOCK_METER_DATA,
    MOCK_OTA_CHECK_NO_UPDATE,
    MOCK_OTA_CHECK_UPDATE,
    MOCK_SYSTEM_INFO,
)

ENTITY_ID = "update.haushalt_test_firmware"


async def _setup_integration(hass: HomeAssistant, mock_config_entry, ota_data=None):
    """Set up the integration with given OTA data."""
    with patch(
        "custom_components.wattwaechter.WattwaechterApiClient"
    ) as mock_cls:
        client = mock_cls.return_value
        client.async_alive = AsyncMock(return_value=MOCK_ALIVE_RESPONSE)
        client.async_get_meter_data = AsyncMock(return_value=MOCK_METER_DATA)
        client.async_get_system_info = AsyncMock(return_value=MOCK_SYSTEM_INFO)
        client.async_check_ota = AsyncMock(
            return_value=ota_data or MOCK_OTA_CHECK_NO_UPDATE
        )
        client.async_start_ota = AsyncMock(return_value={"ok": True})
        client.host = "192.168.1.100"

        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        # Trigger entity poll so OTA data is populated
        await hass.services.async_call(
            "homeassistant",
            "update_entity",
            {"entity_id": ENTITY_ID},
            blocking=True,
        )
        await hass.async_block_till_done()

        return client


async def test_update_entity_no_update(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test update entity when no firmware update is available."""
    await _setup_integration(hass, mock_config_entry)

    state = hass.states.get(ENTITY_ID)
    assert state is not None
    assert state.attributes["installed_version"] == MOCK_FW_VERSION
    # No update available: latest_version == installed_version
    assert state.attributes["latest_version"] == MOCK_FW_VERSION


async def test_update_entity_update_available(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test update entity when a firmware update is available."""
    await _setup_integration(hass, mock_config_entry, MOCK_OTA_CHECK_UPDATE)

    state = hass.states.get(ENTITY_ID)
    assert state is not None
    assert state.attributes["installed_version"] == MOCK_FW_VERSION
    assert state.attributes["latest_version"] == "2.0.0"


async def test_update_entity_install(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test triggering a firmware update install."""
    client = await _setup_integration(
        hass, mock_config_entry, MOCK_OTA_CHECK_UPDATE
    )

    # Make alive return new version immediately (simulating fast update)
    client.async_alive = AsyncMock(
        return_value={"alive": True, "version": "2.0.0"}
    )

    with patch("custom_components.wattwaechter.update.asyncio.sleep", new_callable=AsyncMock):
        await hass.services.async_call(
            "update",
            "install",
            {"entity_id": ENTITY_ID},
            blocking=True,
        )

    client.async_start_ota.assert_called_once()


async def test_update_entity_install_auth_error(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test firmware update fails with auth error."""
    client = await _setup_integration(
        hass, mock_config_entry, MOCK_OTA_CHECK_UPDATE
    )

    client.async_start_ota = AsyncMock(
        side_effect=WattwaechterAuthError("WRITE token required")
    )

    with pytest.raises(WattwaechterAuthError):
        await hass.services.async_call(
            "update",
            "install",
            {"entity_id": ENTITY_ID},
            blocking=True,
        )


async def test_update_entity_install_connection_error(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test firmware update fails with connection error."""
    client = await _setup_integration(
        hass, mock_config_entry, MOCK_OTA_CHECK_UPDATE
    )

    client.async_start_ota = AsyncMock(
        side_effect=WattwaechterConnectionError("Connection refused")
    )

    with pytest.raises(WattwaechterConnectionError):
        await hass.services.async_call(
            "update",
            "install",
            {"entity_id": ENTITY_ID},
            blocking=True,
        )


async def test_update_entity_reboot_detection(
    hass: HomeAssistant, mock_config_entry
) -> None:
    """Test reboot detection after OTA (device goes offline then online)."""
    client = await _setup_integration(
        hass, mock_config_entry, MOCK_OTA_CHECK_UPDATE
    )

    # Simulate: device goes offline, then comes back
    call_count = 0

    async def alive_side_effect():
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            raise WattwaechterConnectionError("Device offline")
        return {"alive": True, "version": "2.0.0"}

    client.async_alive = AsyncMock(side_effect=alive_side_effect)

    with patch("custom_components.wattwaechter.update.asyncio.sleep", new_callable=AsyncMock):
        await hass.services.async_call(
            "update",
            "install",
            {"entity_id": ENTITY_ID},
            blocking=True,
        )

    client.async_start_ota.assert_called_once()
    # alive was called multiple times during reboot detection
    assert client.async_alive.call_count >= 3
