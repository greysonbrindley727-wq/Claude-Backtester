"""
Metrics, version 1. Percentages are returned as plain numbers (12.3 means 12.3%).
"""
import math

import numpy as np

METRICS_VERSION = "1"


def _pct(x):
    if x is None:
        return None
    x = float(x)
    if math.isnan(x) or math.isinf(x):
        return None
    return round(x * 100, 2)


def compute(equity, trades, start_cash, bars_per_year, benchmark_return=None) -> dict:
    end = float(equity.iloc[-1])
    total = end / start_cash - 1
    max_dd = float((equity / equity.cummax() - 1).min())

    rets = equity.pct_change().dropna()
    if len(rets) > 1 and rets.std() > 0:
        sharpe = float(rets.mean() / rets.std() * math.sqrt(bars_per_year))
    else:
        sharpe = 0.0

    monthly = equity.resample("ME").last()
    prev = monthly.shift(1)
    prev.iloc[0] = start_cash
    month_ret = monthly / prev - 1

    pnls = [t["pnl"] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    gross_win = float(sum(wins))
    gross_loss = float(-sum(losses))
    profit_factor = gross_win / gross_loss if gross_loss > 0 else None

    out = {
        "total_return_pct": _pct(total),
        "end_equity": round(end, 2),
        "max_drawdown_pct": _pct(max_dd),
        "sharpe": round(sharpe, 2),
        "trades": len(pnls),
        "win_rate_pct": _pct(len(wins) / len(pnls)) if pnls else None,
        "profit_factor": round(profit_factor, 2) if profit_factor is not None else None,
        "avg_trade_pnl": round(float(np.mean(pnls)), 2) if pnls else None,
        "pct_months_profitable": _pct((month_ret > 0).mean()) if len(month_ret) else None,
        "worst_month_pct": _pct(month_ret.min()) if len(month_ret) else None,
    }
    if benchmark_return is not None:
        out["benchmark_return_pct"] = _pct(benchmark_return)
        out["vs_benchmark_pct"] = _pct(total - benchmark_return)
    return out
