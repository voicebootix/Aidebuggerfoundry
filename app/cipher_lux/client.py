"""
CipherLux REST API client.

Authentication: Firebase ID token passed as  Authorization: Bearer <token>
Base URL is read from CIPHERLUX_BASE_URL env var, or supplied per-request.
"""

import asyncio
import logging
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class CipherLuxError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"CipherLux API {status_code}: {detail}")


class CipherLuxClient:
    """Async context-manager client for the CipherLux REST API."""

    def __init__(self, base_url: str, token: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout
        self._http: Optional[httpx.AsyncClient] = None

    # ── lifecycle ────────────────────────────────────────────────────────────

    async def __aenter__(self) -> "CipherLuxClient":
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            },
            timeout=self._timeout,
        )
        return self

    async def __aexit__(self, *_) -> None:
        if self._http:
            await self._http.aclose()

    def _client(self) -> httpx.AsyncClient:
        if self._http is None:
            raise RuntimeError("Use CipherLuxClient as an async context manager.")
        return self._http

    def _raise(self, r: httpx.Response) -> None:
        if r.is_error:
            try:
                detail = r.json().get("detail") or r.json().get("message") or r.text
            except Exception:
                detail = r.text
            raise CipherLuxError(r.status_code, detail)

    # ── health ───────────────────────────────────────────────────────────────

    async def health(self) -> dict:
        r = await self._client().get("/health")
        self._raise(r)
        return r.json()

    async def ready(self) -> dict:
        r = await self._client().get("/ready")
        self._raise(r)
        return r.json()

    async def version(self) -> dict:
        r = await self._client().get("/version")
        self._raise(r)
        return r.json()

    # ── strategies ───────────────────────────────────────────────────────────

    async def list_strategies(self) -> list:
        r = await self._client().get("/v1/strategies")
        self._raise(r)
        data = r.json()
        return data if isinstance(data, list) else data.get("strategies", data.get("data", []))

    async def get_strategy(self, strategy_id: str) -> dict:
        r = await self._client().get(f"/v1/strategies/{strategy_id}")
        self._raise(r)
        return r.json()

    async def create_strategy(self, name: str, code: str, parameters: dict | None = None) -> dict:
        payload: dict[str, Any] = {"name": name, "code": code}
        if parameters:
            payload["parameters"] = parameters
        r = await self._client().post("/v1/strategies", json=payload)
        self._raise(r)
        return r.json()

    async def save_strategy(self, strategy_id: str, code: str, parameters: dict | None = None) -> dict:
        payload: dict[str, Any] = {"code": code}
        if parameters:
            payload["parameters"] = parameters
        r = await self._client().put(f"/v1/strategies/{strategy_id}", json=payload)
        self._raise(r)
        return r.json()

    async def delete_strategy(self, strategy_id: str) -> dict:
        r = await self._client().delete(f"/v1/strategies/{strategy_id}")
        self._raise(r)
        return r.json()

    # ── backtesting ──────────────────────────────────────────────────────────

    async def run_backtest(self, strategy_id: str, config: dict | None = None) -> dict:
        """Trigger a backtest. Returns a response that includes a backtest ID."""
        r = await self._client().post(
            f"/v1/strategies/{strategy_id}/backtest",
            json=config or {},
        )
        self._raise(r)
        return r.json()

    async def get_backtest_result(self, strategy_id: str, backtest_id: str) -> dict:
        r = await self._client().get(
            f"/v1/strategies/{strategy_id}/backtest/{backtest_id}"
        )
        self._raise(r)
        return r.json()

    async def poll_backtest(
        self,
        strategy_id: str,
        backtest_id: str,
        timeout: int = 300,
        interval: int = 5,
    ) -> dict:
        """Poll until backtest reaches a terminal state or timeout is exceeded."""
        elapsed = 0
        while elapsed < timeout:
            result = await self.get_backtest_result(strategy_id, backtest_id)
            status = (result.get("status") or "").lower()
            if status in {"completed", "done", "success", "failed", "error"}:
                logger.info(f"Backtest {backtest_id} finished with status={status}")
                return result
            logger.debug(f"Backtest {backtest_id} status={status}, waiting {interval}s …")
            await asyncio.sleep(interval)
            elapsed += interval
        raise TimeoutError(f"Backtest {backtest_id} did not complete within {timeout}s")

    # ── publishing ───────────────────────────────────────────────────────────

    async def publish_strategy(self, strategy_id: str) -> dict:
        r = await self._client().post(f"/v1/strategies/{strategy_id}/publish")
        self._raise(r)
        return r.json()

    # ── IDE / projects ───────────────────────────────────────────────────────

    async def list_projects(self) -> list:
        r = await self._client().get("/v1/ide/projects")
        self._raise(r)
        data = r.json()
        return data if isinstance(data, list) else data.get("projects", data.get("data", []))

    async def create_project(self, name: str) -> dict:
        r = await self._client().post("/v1/ide/projects", json={"name": name})
        self._raise(r)
        return r.json()

    async def create_file(self, project_id: str, filename: str, content: str) -> dict:
        r = await self._client().post(
            f"/v1/ide/projects/{project_id}/files",
            json={"name": filename, "content": content},
        )
        self._raise(r)
        return r.json()

    async def update_file(self, project_id: str, file_id: str, content: str) -> dict:
        r = await self._client().put(
            f"/v1/ide/projects/{project_id}/files/{file_id}",
            json={"content": content},
        )
        self._raise(r)
        return r.json()
