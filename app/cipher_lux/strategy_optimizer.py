"""
Grid-search optimizer for CipherLux strategies.

Flow:
  1. Expand param_grid into all combinations (capped at max_iterations).
  2. For each combo: inject params into code → create strategy → backtest → score.
  3. Return the best-scoring (params, metrics) pair plus a full results log.

Params are injected as top-of-file constants so the strategy code can reference
them by name without modification.  Example strategy code head:

    period = 20           # ← injected by optimizer
    threshold = 0.02      # ← injected by optimizer
    ...
"""

from __future__ import annotations

import asyncio
import itertools
import logging
from typing import Any, Callable, Optional

from .client import CipherLuxClient, CipherLuxError
from .backtest_analyzer import BacktestMetrics, parse_backtest_results

logger = logging.getLogger(__name__)


OptResultLog = list[dict]   # [{params, metrics_summary, score}]


async def optimize_strategy(
    client: CipherLuxClient,
    base_code: str,
    param_grid: dict[str, list],
    *,
    strategy_name: str = "optimized_strategy",
    backtest_config: dict | None = None,
    backtest_timeout: int = 300,
    max_iterations: int = 50,
    on_iteration: Optional[Callable[[int, int, dict, BacktestMetrics], None]] = None,
) -> tuple[dict, BacktestMetrics, OptResultLog]:
    """
    Run a grid-search optimization.

    Args:
        client:           Authenticated CipherLuxClient (must be open — use as async-cm).
        base_code:        Raw Python strategy source. Params are prepended as constants.
        param_grid:       {"period": [10, 20, 50], "threshold": [0.01, 0.02]}
        strategy_name:    Base name for created strategies.
        backtest_config:  Extra JSON body for the /backtest endpoint.
        backtest_timeout: Per-iteration poll timeout in seconds.
        max_iterations:   Cap on total combinations tested.
        on_iteration:     Optional async callback(current, total, params, metrics).

    Returns:
        (best_params, best_metrics, results_log)
    """
    keys = list(param_grid.keys())
    combos: list[tuple] = list(itertools.product(*param_grid.values()))[:max_iterations]
    total = len(combos)
    logger.info(f"Optimization starting: {total} combinations, params={keys}")

    best_params: dict = {}
    best_metrics: Optional[BacktestMetrics] = None
    results_log: OptResultLog = []

    for idx, combo in enumerate(combos, start=1):
        params = dict(zip(keys, combo))
        logger.info(f"[{idx}/{total}] params={params}")

        try:
            code = _inject_params(base_code, params)

            strategy = await client.create_strategy(
                name=f"{strategy_name}_opt_{idx}",
                code=code,
                parameters=params,
            )
            sid = _extract_id(strategy, ("id", "strategyId", "strategy_id"))

            bt_response = await client.run_backtest(sid, backtest_config or {})
            bt_id = _extract_id(bt_response, ("id", "backtestId", "backtest_id", "jobId"))

            raw = await client.poll_backtest(sid, bt_id, timeout=backtest_timeout)

            status = (raw.get("status") or "").lower()
            if status in {"failed", "error"}:
                logger.warning(f"  Backtest failed: {raw.get('error') or raw.get('message')}")
                results_log.append({"params": params, "status": "failed"})
                continue

            metrics = parse_backtest_results(raw)
            entry = {
                "iteration": idx,
                "params": params,
                "metrics": metrics.summary(),
                "score": metrics.score,
                "status": "completed",
            }
            results_log.append(entry)

            if on_iteration:
                try:
                    await on_iteration(idx, total, params, metrics)
                except Exception as cb_err:
                    logger.warning(f"on_iteration callback error: {cb_err}")

            if best_metrics is None or metrics.score > best_metrics.score:
                best_metrics = metrics
                best_params = params
                logger.info(
                    f"  ★ New best  score={metrics.score:.4f}  "
                    f"sharpe={metrics.sharpe_ratio:.3f}  "
                    f"pf={metrics.profit_factor:.3f}  "
                    f"dd={metrics.max_drawdown:.2%}"
                )

        except TimeoutError:
            logger.error(f"  Backtest timed out for params={params}")
            results_log.append({"params": params, "status": "timeout"})
        except CipherLuxError as e:
            logger.error(f"  API error {e.status_code}: {e.detail}")
            results_log.append({"params": params, "status": "api_error", "detail": e.detail})
        except Exception as e:
            logger.error(f"  Unexpected error: {e}", exc_info=True)
            results_log.append({"params": params, "status": "error", "detail": str(e)})

    if best_metrics is None:
        raise RuntimeError("Every backtest iteration failed — no valid result produced.")

    logger.info(
        f"Optimization complete. "
        f"Best params={best_params}  score={best_metrics.score:.4f}"
    )
    return best_params, best_metrics, results_log


# ── helpers ───────────────────────────────────────────────────────────────────

def _inject_params(code: str, params: dict) -> str:
    """Prepend parameter constants so the strategy code can use them by name."""
    lines = ["# === Optimizer-injected parameters ==="]
    for k, v in params.items():
        if isinstance(v, str):
            lines.append(f'{k} = "{v}"')
        else:
            lines.append(f"{k} = {v}")
    lines.append("# =====================================\n")
    return "\n".join(lines) + "\n" + code


def _extract_id(obj: dict, keys: tuple[str, ...]) -> str:
    for k in keys:
        if k in obj and obj[k] is not None:
            return str(obj[k])
    raise KeyError(f"Cannot find an ID field in response. Tried: {keys}. Got: {list(obj.keys())}")
