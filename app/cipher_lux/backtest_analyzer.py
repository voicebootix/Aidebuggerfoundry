"""
Parse and score CipherLux backtest results.

Handles the common camelCase / snake_case / TradingView-style field aliases
that trading platforms emit, so callers don't need to care.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Aliases: normalized name → list of raw field names to try
_FIELD_MAP: dict[str, list[str]] = {
    "total_return":    ["total_return", "totalReturn", "net_profit_pct", "netProfitPct", "total_pnl_pct"],
    "annual_return":   ["annual_return", "annualReturn", "cagr", "annualized_return"],
    "max_drawdown":    ["max_drawdown", "maxDrawdown", "maximum_drawdown", "maxDD"],
    "sharpe_ratio":    ["sharpe_ratio", "sharpeRatio", "sharpe"],
    "sortino_ratio":   ["sortino_ratio", "sortinoRatio", "sortino"],
    "win_rate":        ["win_rate", "winRate", "percent_profitable", "percentProfitable"],
    "profit_factor":   ["profit_factor", "profitFactor", "pf"],
    "total_trades":    ["total_trades", "totalTrades", "num_trades", "numTrades", "closed_trades"],
    "avg_trade_return":["avg_trade_return", "avgTradeReturn", "avg_profit_pct", "averageTradeReturn"],
    "expectancy":      ["expectancy", "expected_value", "expectedValue"],
}


@dataclass
class BacktestMetrics:
    total_return: float = 0.0
    annual_return: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_trades: int = 0
    avg_trade_return: float = 0.0
    expectancy: float = 0.0
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def score(self) -> float:
        """
        Composite optimization score — higher is better.
        Balances Sharpe, profit factor, and win rate while penalising drawdown.
        Returns -999 for degenerate results.
        """
        if self.max_drawdown >= 1.0 or self.profit_factor <= 0 or self.total_trades < 5:
            return -999.0
        # Normalise drawdown penalty (0 at 0%, full weight at 50%+)
        dd_penalty = min(self.max_drawdown / 0.50, 1.0)
        return (
            self.sharpe_ratio   * 0.35
            + self.profit_factor  * 0.30
            + self.win_rate       * 0.20
            - dd_penalty          * 0.15
        )

    def summary(self) -> dict:
        return {
            "total_return":    f"{self.total_return:.2%}",
            "annual_return":   f"{self.annual_return:.2%}",
            "max_drawdown":    f"{self.max_drawdown:.2%}",
            "sharpe_ratio":    round(self.sharpe_ratio, 4),
            "sortino_ratio":   round(self.sortino_ratio, 4),
            "win_rate":        f"{self.win_rate:.2%}",
            "profit_factor":   round(self.profit_factor, 4),
            "total_trades":    self.total_trades,
            "avg_trade_return":f"{self.avg_trade_return:.4%}",
            "composite_score": round(self.score, 4),
        }

    def improvement_suggestions(self) -> list[str]:
        """Return human-readable hints to guide the next optimization round."""
        hints = []
        if self.sharpe_ratio < 1.0:
            hints.append("Sharpe < 1 — reduce volatility or improve consistency.")
        if self.max_drawdown > 0.20:
            hints.append("Max drawdown > 20% — add a stop-loss or tighten position sizing.")
        if self.win_rate < 0.40:
            hints.append("Win rate < 40% — reconsider entry signals or add a filter.")
        if self.profit_factor < 1.5:
            hints.append("Profit factor < 1.5 — improve reward-to-risk ratio per trade.")
        if self.total_trades < 30:
            hints.append("Too few trades for statistical confidence — loosen entry conditions.")
        if not hints:
            hints.append("Metrics look solid. Consider forward-testing on unseen data.")
        return hints


def parse_backtest_results(raw: dict) -> BacktestMetrics:
    """Extract standardised metrics from any CipherLux backtest response shape."""
    # CipherLux may nest metrics under a sub-key
    metrics_blob: dict = raw
    for key in ("metrics", "results", "performance", "data"):
        if isinstance(raw.get(key), dict):
            metrics_blob = raw[key]
            break

    def _get(field: str) -> float:
        for alias in _FIELD_MAP.get(field, []):
            val = metrics_blob.get(alias)
            if val is not None:
                try:
                    return float(val)
                except (TypeError, ValueError):
                    pass
        return 0.0

    trades = int(_get("total_trades"))
    return BacktestMetrics(
        total_return=_get("total_return"),
        annual_return=_get("annual_return"),
        max_drawdown=_get("max_drawdown"),
        sharpe_ratio=_get("sharpe_ratio"),
        sortino_ratio=_get("sortino_ratio"),
        win_rate=_get("win_rate"),
        profit_factor=_get("profit_factor"),
        total_trades=trades,
        avg_trade_return=_get("avg_trade_return"),
        expectancy=_get("expectancy"),
        raw=raw,
    )
