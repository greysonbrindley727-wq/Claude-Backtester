"""
Batch backtester runner, version 1.

Runs every strategy in strategies/ on every symbol in config.json. Each one runs
in-sample (the earlier part of history) and out-of-sample (the last holdout_fraction,
which the screen never tuned on). Costs are applied. Each run is repeated with
slippage multiplied as a stress test. Writes to results/:
  backtest-<date>.json    full detail, including equity curves and trades
  leaderboard-<date>.csv  one row per strategy, sorted by out-of-sample return
  details-<date>.csv      one row per strategy, symbol and period

Usage: python run_backtests.py [--config config.json] [--data-dir data] [--out-dir results]
"""
import argparse
import dataclasses
import datetime as dt
import json
import math
import os

import numpy as np
import pandas as pd

import engine
import metrics
from data import load_bars
from strategies import ALL_STRATEGIES

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER_VERSION = "1"


def clean(obj):
    """Make values JSON-safe."""
    if isinstance(obj, dict):
        return {k: clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean(v) for v in obj]
    if isinstance(obj, (pd.Timestamp, dt.datetime, dt.date)):
        return obj.isoformat()
    if isinstance(obj, np.generic):
        obj = obj.item()
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def run_strategy(strategy, bars, cfg, costs, stress_costs):
    runs = []
    bench_close = bars[cfg["benchmark"]]["close"]
    for symbol in cfg["symbols"]:
        df = bars[symbol]
        if len(df) < 50:
            continue
        desired = strategy.signals(df).shift(1).fillna(0).astype(int)
        cut = df.index[int(len(df) * (1 - cfg["holdout_fraction"]))]
        periods = (("in_sample", df.index < cut), ("out_of_sample", df.index >= cut))
        for period, mask in periods:
            d, des = df[mask], desired[mask]
            if len(d) < 2:
                continue
            bpy = engine.bars_per_year(d.index)
            bench = bench_close.reindex(d.index, method="ffill").dropna()
            bench_ret = float(bench.iloc[-1] / bench.iloc[0] - 1) if len(bench) > 1 else None

            res = engine.run(d, des, costs, strategy.position_fraction)
            m = metrics.compute(res["equity"], res["trades"], costs.starting_cash, bpy, bench_ret)

            st = engine.run(d, des, stress_costs, strategy.position_fraction)
            sm = metrics.compute(st["equity"], st["trades"], stress_costs.starting_cash, bpy)
            m["stress_total_return_pct"] = sm["total_return_pct"]
            m["stress_win_rate_pct"] = sm["win_rate_pct"]

            daily = res["equity"].resample("D").last().dropna()
            runs.append({
                "strategy": strategy.name,
                "version": strategy.version,
                "symbol": symbol,
                "period": period,
                "period_start": d.index[0],
                "period_end": d.index[-1],
                "metrics": m,
                "equity_daily": [[k, round(float(v), 2)] for k, v in daily.items()],
                "trades": res["trades"],
            })
    return runs


def leaderboard(runs):
    flat = pd.DataFrame([{"strategy": r["strategy"], "version": r["version"],
                          "symbol": r["symbol"], "period": r["period"], **r["metrics"]}
                         for r in runs])
    if flat.empty:
        return []

    def avg(frame, col):
        v = pd.to_numeric(frame[col], errors="coerce").mean()
        return None if pd.isna(v) else round(float(v), 2)

    board = []
    for name, g in flat.groupby("strategy", sort=False):
        oos = g[g.period == "out_of_sample"]
        ins = g[g.period == "in_sample"]
        ret = pd.to_numeric(oos["total_return_pct"], errors="coerce")
        has_ret = bool(ret.notna().any())
        in_mean = avg(ins, "total_return_pct")
        oos_mean = avg(oos, "total_return_pct")
        board.append({
            "strategy": name,
            "version": oos["version"].iloc[0] if len(oos) else g["version"].iloc[0],
            "oos_mean_return_pct": oos_mean,
            "oos_worst_symbol_pct": round(float(ret.min()), 2) if has_ret else None,
            "oos_symbols_profitable_pct": round(float((ret > 0).mean() * 100), 1) if has_ret else None,
            "oos_vs_benchmark_pct": avg(oos, "vs_benchmark_pct"),
            "oos_mean_win_rate_pct": avg(oos, "win_rate_pct"),
            "oos_mean_max_drawdown_pct": avg(oos, "max_drawdown_pct"),
            "oos_mean_sharpe": avg(oos, "sharpe"),
            "oos_mean_pct_months_profitable": avg(oos, "pct_months_profitable"),
            "oos_trades": int(pd.to_numeric(oos["trades"], errors="coerce").sum()),
            "oos_stress_mean_return_pct": avg(oos, "stress_total_return_pct"),
            "in_sample_mean_return_pct": in_mean,
            "overfit_gap_pct": (round(in_mean - oos_mean, 2)
                                if in_mean is not None and oos_mean is not None else None),
        })
    board.sort(key=lambda r: r["oos_mean_return_pct"]
               if r["oos_mean_return_pct"] is not None else -1e9, reverse=True)
    return board


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join(HERE, "config.json"))
    ap.add_argument("--data-dir", default=os.path.join(HERE, "data"))
    ap.add_argument("--out-dir", default=os.path.join(HERE, "results"))
    args = ap.parse_args()

    with open(args.config) as f:
        cfg = json.load(f)
    costs = engine.Costs(**cfg["costs"])
    stress_costs = dataclasses.replace(
        costs, slippage_bps=costs.slippage_bps * cfg["stress_slippage_multiplier"])

    needed = list(dict.fromkeys(cfg["symbols"] + [cfg["benchmark"]]))
    bars = {s: load_bars(s, cfg["timeframe"], cfg["start"], cfg["end"], args.data_dir)
            for s in needed}

    runs, strategies_info = [], []
    for cls in ALL_STRATEGIES:
        strat = cls()
        strategies_info.append(strat.describe())
        runs += run_strategy(strat, bars, cfg, costs, stress_costs)
        print(f"done: {strat.name}")

    board = leaderboard(runs)
    stamp = dt.date.today().isoformat()
    os.makedirs(args.out_dir, exist_ok=True)

    payload = {
        "runner_version": RUNNER_VERSION,
        "engine_version": engine.ENGINE_VERSION,
        "metrics_version": metrics.METRICS_VERSION,
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "config": cfg,
        "strategies": strategies_info,
        "leaderboard": board,
        "runs": runs,
    }
    with open(os.path.join(args.out_dir, f"backtest-{stamp}.json"), "w") as f:
        json.dump(clean(payload), f, indent=2)
    pd.DataFrame(board).to_csv(os.path.join(args.out_dir, f"leaderboard-{stamp}.csv"), index=False)
    details = pd.DataFrame([{"strategy": r["strategy"], "version": r["version"],
                             "symbol": r["symbol"], "period": r["period"], **r["metrics"]}
                            for r in runs])
    details.to_csv(os.path.join(args.out_dir, f"details-{stamp}.csv"), index=False)

    print(pd.DataFrame(board).to_string(index=False))


if __name__ == "__main__":
    main()
