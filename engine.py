"""
Simulation engine, version 1.

Rules:
- A position decided at bar i's close is filled at bar i+1's open.
- Every fill is worse than the open by slippage_bps (you always pay the spread).
- Sells pay SEC and FINRA fees. Rates live in config.json, so check current values.
- Shorts pay a borrow fee for as long as they are open.
- Position size is position_fraction of cash at entry, and stays fixed for that trade.
- A trade is one stretch of time in one direction. Reversing counts as a close and a new open.
"""
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

ENGINE_VERSION = "1"


@dataclass
class Costs:
    starting_cash: float = 1000.0
    slippage_bps: float = 2.0
    commission_per_share: float = 0.0        # Alpaca stock commissions are $0
    sec_fee_per_dollar: float = 0.0000278    # on sells
    finra_taf_per_share: float = 0.000166    # on sells
    finra_taf_max: float = 8.30              # per sell order
    borrow_rate_annual: float = 0.01         # on shorts


def bars_per_year(index) -> float:
    """Average number of bars per year, measured from the data itself."""
    if len(index) < 2:
        return 252.0
    years = (index[-1] - index[0]).total_seconds() / (365.25 * 86400)
    return len(index) / years if years > 0 else 252.0


def _fill(delta, price, c: Costs):
    """Trade `delta` shares (signed). Returns (cash change, fill price, fees)."""
    n = abs(delta)
    slip = c.slippage_bps / 10000
    if delta > 0:
        fill = price * (1 + slip)
        fees = n * c.commission_per_share
        return -(n * fill + fees), fill, fees
    fill = price * (1 - slip)
    proceeds = n * fill
    fees = (n * c.commission_per_share
            + proceeds * c.sec_fee_per_dollar
            + min(n * c.finra_taf_per_share, c.finra_taf_max))
    return proceeds - fees, fill, fees


def run(df, desired, costs: Costs, position_fraction: float = 1.0) -> dict:
    """
    df: bars with open and close columns.
    desired: the position to hold on each bar, already shifted so it was known before that bar opened.
    Returns {"equity": Series, "trades": list of dicts}.
    """
    idx = df.index
    n = len(df)
    desired = np.asarray(desired).astype(int)
    opens = df["open"].to_numpy(float)
    closes = df["close"].to_numpy(float)
    borrow_per_bar = costs.borrow_rate_annual / bars_per_year(idx)

    cash = costs.starting_cash
    qty = 0
    trade = None
    trades = []
    equity = np.empty(n)

    for i in range(n):
        if qty < 0:
            cash -= abs(qty) * closes[i] * borrow_per_bar

        want = int(desired[i])
        cur = int(np.sign(qty))
        if want != cur:
            if qty != 0:
                d, fill, _ = _fill(-qty, opens[i], costs)
                cash += d
                trade.update(exit_time=idx[i], exit_price=fill,
                             pnl=cash - trade.pop("cash_before"))
                trades.append(trade)
                trade = None
                qty = 0
            if want != 0:
                price_with_slip = opens[i] * (1 + costs.slippage_bps / 10000)
                shares = math.floor(cash * position_fraction / price_with_slip) * want
                if shares != 0:
                    cash_before = cash
                    d, fill, _ = _fill(shares, opens[i], costs)
                    cash += d
                    qty = shares
                    trade = {"direction": "long" if want > 0 else "short",
                             "entry_time": idx[i], "entry_price": fill,
                             "shares": abs(shares), "cash_before": cash_before}

        equity[i] = cash + qty * closes[i]

    if qty != 0:  # close anything still open at the end of the data
        d, fill, _ = _fill(-qty, closes[-1], costs)
        cash += d
        trade.update(exit_time=idx[-1], exit_price=fill, pnl=cash - trade.pop("cash_before"))
        trades.append(trade)
        qty = 0
        equity[-1] = cash

    return {"equity": pd.Series(equity, index=idx, name="equity"), "trades": trades}
