"""Tests for the WattWächter Plus API client."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.wattwaechter.api import (
    WattwaechterApiClient,
    WattwaechterAuthError,
    WattwaechterConnectionError,
)


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    return MagicMock(spec=aiohttp.ClientSession)


def _mock_response(status: int, json_data: dict | None = None):
    """Create a mock aiohttp response."""
    resp = AsyncMock()
    resp.status = status
    if json_data is not None:
        resp.json = AsyncMock(return_value=json_data)
    return resp


async def test_alive(mock_session) -> None:
    """Test alive endpoint (no auth)."""
    mock_session.request = AsyncMock(
        return_value=_mock_response(200, {"alive": True, "version": "1.2.3"})
    )
    client = WattwaechterApiClient("192.168.1.100", mock_session, "token")
    result = await client.async_alive()

    assert result["alive"] is True
    assert result["version"] == "1.2.3"
    # Alive should not send auth headers
    call_args = mock_session.request.call_args
    assert "Authorization" not in call_args.kwargs.get("headers", {})


async def test_get_meter_data(mock_session) -> None:
    """Test meter data endpoint."""
    meter_data = {"1.8.0": {"value": 100.0, "unit": "kWh"}}
    mock_session.request = AsyncMock(
        return_value=_mock_response(200, meter_data)
    )
    client = WattwaechterApiClient("192.168.1.100", mock_session, "token")
    result = await client.async_get_meter_data()

    assert result == meter_data


async def test_get_meter_data_204(mock_session) -> None:
    """Test meter data endpoint returns None on HTTP 204."""
    mock_session.request = AsyncMock(return_value=_mock_response(204))
    client = WattwaechterApiClient("192.168.1.100", mock_session, "token")
    result = await client.async_get_meter_data()

    assert result is None


async def test_get_system_info(mock_session) -> None:
    """Test system info endpoint."""
    sys_info = {"esp": [{"name": "esp_id", "value": "ABC123"}]}
    mock_session.request = AsyncMock(
        return_value=_mock_response(200, sys_info)
    )
    client = WattwaechterApiClient("192.168.1.100", mock_session, "token")
    result = await client.async_get_system_info()

    assert result == sys_info


async def test_auth_error(mock_session) -> None:
    """Test that HTTP 401 raises WattwaechterAuthError."""
    mock_session.request = AsyncMock(return_value=_mock_response(401))
    client = WattwaechterApiClient("192.168.1.100", mock_session, "bad-token")

    with pytest.raises(WattwaechterAuthError):
        await client.async_get_system_info()


async def test_connection_error_on_timeout(mock_session) -> None:
    """Test that timeout raises WattwaechterConnectionError."""
    mock_session.request = AsyncMock(side_effect=asyncio.TimeoutError())
    client = WattwaechterApiClient("192.168.1.100", mock_session)

    with pytest.raises(WattwaechterConnectionError):
        await client.async_alive()


async def test_connection_error_on_client_error(mock_session) -> None:
    """Test that aiohttp errors raise WattwaechterConnectionError."""
    mock_session.request = AsyncMock(
        side_effect=aiohttp.ClientError("Connection refused")
    )
    client = WattwaechterApiClient("192.168.1.100", mock_session)

    with pytest.raises(WattwaechterConnectionError):
        await client.async_alive()


async def test_unexpected_status_code(mock_session) -> None:
    """Test that unexpected HTTP status raises WattwaechterConnectionError."""
    mock_session.request = AsyncMock(return_value=_mock_response(500))
    client = WattwaechterApiClient("192.168.1.100", mock_session, "token")

    with pytest.raises(WattwaechterConnectionError, match="Unexpected status 500"):
        await client.async_get_system_info()


async def test_invalid_json_response(mock_session) -> None:
    """Test that invalid JSON raises WattwaechterConnectionError."""
    resp = _mock_response(200)
    resp.json = AsyncMock(side_effect=aiohttp.ContentTypeError(MagicMock(), MagicMock()))
    mock_session.request = AsyncMock(return_value=resp)
    client = WattwaechterApiClient("192.168.1.100", mock_session)

    with pytest.raises(WattwaechterConnectionError, match="Invalid JSON"):
        await client.async_alive()


async def test_auth_header_with_token(mock_session) -> None:
    """Test that auth header is sent when token is provided."""
    mock_session.request = AsyncMock(
        return_value=_mock_response(200, {"ok": True})
    )
    client = WattwaechterApiClient("192.168.1.100", mock_session, "my-token")
    await client.async_get_system_info()

    call_args = mock_session.request.call_args
    assert call_args.kwargs["headers"]["Authorization"] == "Bearer my-token"


async def test_no_auth_header_without_token(mock_session) -> None:
    """Test that no auth header is sent when token is None."""
    mock_session.request = AsyncMock(
        return_value=_mock_response(200, {"ok": True})
    )
    client = WattwaechterApiClient("192.168.1.100", mock_session)
    await client.async_get_system_info()

    call_args = mock_session.request.call_args
    assert "Authorization" not in call_args.kwargs.get("headers", {})


async def test_check_ota(mock_session) -> None:
    """Test OTA check endpoint."""
    ota_data = {"ok": True, "data": {"update_available": True, "version": "2.0.0"}}
    mock_session.request = AsyncMock(
        return_value=_mock_response(200, ota_data)
    )
    client = WattwaechterApiClient("192.168.1.100", mock_session, "token")
    result = await client.async_check_ota()

    assert result["data"]["update_available"] is True
    assert result["data"]["version"] == "2.0.0"


async def test_start_ota(mock_session) -> None:
    """Test OTA start endpoint uses POST."""
    mock_session.request = AsyncMock(
        return_value=_mock_response(200, {"ok": True})
    )
    client = WattwaechterApiClient("192.168.1.100", mock_session, "token")
    await client.async_start_ota()

    call_args = mock_session.request.call_args
    assert call_args.args[0] == "POST"
