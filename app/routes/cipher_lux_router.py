"""
CipherLux integration router.

All endpoints require a CipherLux Firebase Bearer token, supplied either via:
  • X-CipherLux-Token  header  (preferred, per-request)
  • CIPHERLUX_FIREBASE_TOKEN   env var / settings (fallback)

The base URL is read from CIPHERLUX_BASE_URL (settings) and can be overridden
per-request via the X-CipherLux-Base-Url header for multi-environment support.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Body
from pydantic import BaseModel, Field

from app.cipher_lux.client import CipherLuxClient, CipherLuxError
from app.cipher_lux.backtest_analyzer import parse_backtest_results
from app.cipher_lux.strategy_optimizer import optimize_strategy
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# ── in-memory job store for long-running optimization jobs ────────────────────
_opt_jobs: dict[str, dict] = {}


# ── dependency helpers ────────────────────────────────────────────────────────

def _resolve_token(header_token: Optional[str]) -> str:
    token = header_token or getattr(settings, "CIPHERLUX_FIREBASE_TOKEN", None)
    if not token:
        raise HTTPException(
            status_code=401,
            detail=(
                "CipherLux token required. "
                "Set X-CipherLux-Token header or CIPHERLUX_FIREBASE_TOKEN env var."
            ),
        )
    return token


def _resolve_base_url(header_url: Optional[str]) -> str:
    url = header_url or getattr(settings, "CIPHERLUX_BASE_URL", None)
    if not url:
        raise HTTPException(
            status_code=400,
            detail=(
                "CipherLux base URL required. "
                "Set X-CipherLux-Base-Url header or CIPHERLUX_BASE_URL env var."
            ),
        )
    return url


def _client(token: str, base_url: str) -> CipherLuxClient:
    return CipherLuxClient(base_url=base_url, token=token)


# ── Pydantic models ───────────────────────────────────────────────────────────

class CreateStrategyRequest(BaseModel):
    name: str = Field(..., description="Strategy display name")
    code: str = Field(..., description="Python strategy source code")
    parameters: Optional[dict] = Field(None, description="Initial parameter values")


class SaveStrategyRequest(BaseModel):
    code: str
    parameters: Optional[dict] = None


class BacktestRequest(BaseModel):
    config: dict = Field(default_factory=dict, description="Extra backtest configuration")


class OptimizeRequest(BaseModel):
    strategy_name: str = Field("my_strategy", description="Base name for created strategies")
    base_code: str = Field(..., description="Python strategy source code (params injected at top)")
    param_grid: dict[str, list] = Field(
        ...,
        description="Parameter search space. Example: {\"period\": [10, 20, 50]}",
        examples=[{"period": [10, 20, 50], "threshold": [0.01, 0.02]}],
    )
    backtest_config: dict = Field(default_factory=dict)
    max_iterations: int = Field(50, ge=1, le=500)
    backtest_timeout: int = Field(300, ge=30, le=1800)
    auto_publish: bool = Field(False, description="Publish the best strategy automatically")


class PublishRequest(BaseModel):
    strategy_id: str


# ── endpoints ─────────────────────────────────────────────────────────────────

@router.get("/health", summary="Test CipherLux API connectivity")
async def cipher_health(
    x_cipherlux_token: Optional[str] = Header(None),
    x_cipherlux_base_url: Optional[str] = Header(None),
):
    token = _resolve_token(x_cipherlux_token)
    base_url = _resolve_base_url(x_cipherlux_base_url)
    try:
        async with _client(token, base_url) as c:
            health = await c.health()
            version = {}
            try:
                version = await c.version()
            except Exception:
                pass
        return {"status": "connected", "cipherlux_health": health, "version": version}
    except CipherLuxError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/strategies", summary="List all strategies")
async def list_strategies(
    x_cipherlux_token: Optional[str] = Header(None),
    x_cipherlux_base_url: Optional[str] = Header(None),
):
    token = _resolve_token(x_cipherlux_token)
    base_url = _resolve_base_url(x_cipherlux_base_url)
    try:
        async with _client(token, base_url) as c:
            return {"strategies": await c.list_strategies()}
    except CipherLuxError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/strategies/{strategy_id}", summary="Get a strategy")
async def get_strategy(
    strategy_id: str,
    x_cipherlux_token: Optional[str] = Header(None),
    x_cipherlux_base_url: Optional[str] = Header(None),
):
    token = _resolve_token(x_cipherlux_token)
    base_url = _resolve_base_url(x_cipherlux_base_url)
    try:
        async with _client(token, base_url) as c:
            return await c.get_strategy(strategy_id)
    except CipherLuxError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/strategies", summary="Create a new strategy")
async def create_strategy(
    body: CreateStrategyRequest,
    x_cipherlux_token: Optional[str] = Header(None),
    x_cipherlux_base_url: Optional[str] = Header(None),
):
    token = _resolve_token(x_cipherlux_token)
    base_url = _resolve_base_url(x_cipherlux_base_url)
    try:
        async with _client(token, base_url) as c:
            return await c.create_strategy(body.name, body.code, body.parameters)
    except CipherLuxError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put("/strategies/{strategy_id}", summary="Save / update a strategy")
async def save_strategy(
    strategy_id: str,
    body: SaveStrategyRequest,
    x_cipherlux_token: Optional[str] = Header(None),
    x_cipherlux_base_url: Optional[str] = Header(None),
):
    token = _resolve_token(x_cipherlux_token)
    base_url = _resolve_base_url(x_cipherlux_base_url)
    try:
        async with _client(token, base_url) as c:
            return await c.save_strategy(strategy_id, body.code, body.parameters)
    except CipherLuxError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/strategies/{strategy_id}/backtest", summary="Trigger a backtest")
async def run_backtest(
    strategy_id: str,
    body: BacktestRequest = Body(default_factory=BacktestRequest),
    x_cipherlux_token: Optional[str] = Header(None),
    x_cipherlux_base_url: Optional[str] = Header(None),
):
    token = _resolve_token(x_cipherlux_token)
    base_url = _resolve_base_url(x_cipherlux_base_url)
    try:
        async with _client(token, base_url) as c:
            return await c.run_backtest(strategy_id, body.config)
    except CipherLuxError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/strategies/{strategy_id}/backtest/{backtest_id}",
    summary="Get backtest results and parsed metrics",
)
async def get_backtest_result(
    strategy_id: str,
    backtest_id: str,
    x_cipherlux_token: Optional[str] = Header(None),
    x_cipherlux_base_url: Optional[str] = Header(None),
):
    token = _resolve_token(x_cipherlux_token)
    base_url = _resolve_base_url(x_cipherlux_base_url)
    try:
        async with _client(token, base_url) as c:
            raw = await c.get_backtest_result(strategy_id, backtest_id)
        metrics = parse_backtest_results(raw)
        return {
            "raw": raw,
            "metrics": metrics.summary(),
            "suggestions": metrics.improvement_suggestions(),
        }
    except CipherLuxError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/strategies/{strategy_id}/publish", summary="Publish a strategy")
async def publish_strategy(
    strategy_id: str,
    x_cipherlux_token: Optional[str] = Header(None),
    x_cipherlux_base_url: Optional[str] = Header(None),
):
    token = _resolve_token(x_cipherlux_token)
    base_url = _resolve_base_url(x_cipherlux_base_url)
    try:
        async with _client(token, base_url) as c:
            return await c.publish_strategy(strategy_id)
    except CipherLuxError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


# ── Optimization (async background job) ──────────────────────────────────────

@router.post("/optimize", summary="Start a parameter optimization job")
async def start_optimization(
    body: OptimizeRequest,
    background_tasks: BackgroundTasks,
    x_cipherlux_token: Optional[str] = Header(None),
    x_cipherlux_base_url: Optional[str] = Header(None),
):
    """
    Kicks off a grid-search optimization in the background.
    Returns a job_id immediately; poll /optimize/{job_id} for results.
    """
    token = _resolve_token(x_cipherlux_token)
    base_url = _resolve_base_url(x_cipherlux_base_url)

    job_id = str(uuid.uuid4())
    _opt_jobs[job_id] = {"status": "running", "progress": 0, "total": 0}

    async def _run():
        try:
            async with _client(token, base_url) as c:
                best_params, best_metrics, results_log = await optimize_strategy(
                    client=c,
                    base_code=body.base_code,
                    param_grid=body.param_grid,
                    strategy_name=body.strategy_name,
                    backtest_config=body.backtest_config,
                    max_iterations=body.max_iterations,
                    backtest_timeout=body.backtest_timeout,
                    on_iteration=lambda i, total, p, m: _update_progress(job_id, i, total),
                )
            best_summary = best_metrics.summary()
            best_suggestions = best_metrics.improvement_suggestions()

            published = None
            if body.auto_publish:
                # Find the strategy that matched best_params in results_log
                best_entry = next(
                    (e for e in results_log if e.get("params") == best_params and e.get("status") == "completed"),
                    None,
                )
                if best_entry:
                    sid = best_entry.get("strategy_id")
                    if sid:
                        async with _client(token, base_url) as c:
                            published = await c.publish_strategy(sid)

            _opt_jobs[job_id] = {
                "status": "completed",
                "best_params": best_params,
                "best_metrics": best_summary,
                "suggestions": best_suggestions,
                "results_log": results_log,
                "published": published,
            }
        except Exception as e:
            logger.error(f"Optimization job {job_id} failed: {e}", exc_info=True)
            _opt_jobs[job_id] = {"status": "failed", "error": str(e)}

    background_tasks.add_task(_run)
    return {"job_id": job_id, "status": "running"}


@router.get("/optimize/{job_id}", summary="Poll an optimization job")
async def get_optimization_result(job_id: str):
    job = _opt_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Optimization job {job_id} not found.")
    return {"job_id": job_id, **job}


def _update_progress(job_id: str, current: int, total: int) -> None:
    if job_id in _opt_jobs:
        _opt_jobs[job_id]["progress"] = current
        _opt_jobs[job_id]["total"] = total
