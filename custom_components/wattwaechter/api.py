"""API client for the WattWächter Plus device."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

API_TIMEOUT = 10


class WattwaechterConnectionError(Exception):
    """Error when device is unreachable."""


class WattwaechterAuthError(Exception):
    """Error when authentication fails."""


class WattwaechterApiClient:
    """API client for WattWächter Plus ESP devices."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        token: str | None = None,
    ) -> None:
        """Initialize the API client."""
        self._host = host
        self._session = session
        self._token = token
        self._base_url = f"http://{host}/api/v1"

    @property
    def host(self) -> str:
        """Return the host."""
        return self._host

    def _headers(self, require_auth: bool = True) -> dict[str, str]:
        """Build request headers."""
        headers: dict[str, str] = {}
        if self._token and require_auth:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        require_auth: bool = True,
        allow_204: bool = False,
    ) -> dict[str, Any] | None:
        """Make an API request."""
        url = f"{self._base_url}{path}"
        try:
            async with asyncio.timeout(API_TIMEOUT):
                resp = await self._session.request(
                    method, url, headers=self._headers(require_auth)
                )
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            raise WattwaechterConnectionError(
                f"Cannot connect to {self._host}: {err}"
            ) from err

        if resp.status == 401:
            raise WattwaechterAuthError("Invalid API token")
        if resp.status == 204 and allow_204:
            return None
        if resp.status != 200:
            raise WattwaechterConnectionError(
                f"Unexpected status {resp.status} from {path}"
            )

        try:
            return await resp.json()
        except (aiohttp.ContentTypeError, ValueError) as err:
            raise WattwaechterConnectionError(
                f"Invalid JSON response from {path}: {err}"
            ) from err

    async def async_alive(self) -> dict[str, Any]:
        """Check device connectivity (no auth required).

        GET /api/v1/system/alive
        Returns: {"alive": bool, "version": str}
        """
        result = await self._request("GET", "/system/alive", require_auth=False)
        assert result is not None
        return result

    async def async_get_meter_data(self) -> dict[str, Any] | None:
        """Get current meter readings.

        GET /api/v1/history/latest
        Returns: {"timestamp": int, "datetime": str, "1-0:X.Y.Z": {"value": float, "unit": str}, ...}
        Returns None on HTTP 204 (no data available yet).
        """
        return await self._request("GET", "/history/latest", allow_204=True)

    async def async_get_system_info(self) -> dict[str, Any]:
        """Get system diagnostic information.

        GET /api/v1/system/info
        Returns: {"uptime": [...], "wifi": [...], "esp": [...], "heap": [...]}
        """
        result = await self._request("GET", "/system/info")
        assert result is not None
        return result

    async def async_check_ota(self) -> dict[str, Any]:
        """Check for firmware updates.

        GET /api/v1/ota/check
        Returns: {"ok": bool, "data": {"update_available": bool, "version": str, ...}}
        """
        result = await self._request("GET", "/ota/check")
        assert result is not None
        return result

    async def async_start_ota(self) -> dict[str, Any]:
        """Start firmware update (requires WRITE token).

        POST /api/v1/ota/start
        Returns immediately, device reboots.
        """
        result = await self._request("POST", "/ota/start")
        assert result is not None
        return result
