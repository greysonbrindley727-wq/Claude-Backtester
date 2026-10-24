"""
Simulation engine, version 2.

Rules:
- A position decided at bar i's close is filled at bar i+1's open.
- Every fill is worse than the price by slippage_bps (you always pay the spread).
- Sells pay SEC and FINRA fees. Rates live in config.json, so check current values.
- Shorts pay a borrow fee for as long as they are open.
- Position size is position_fraction of cash at entry, and stays fixed for that trade.
- A trade is one stretch of time in one direction. Reversing counts as a close and a new open.
- Stop-loss and take-profit (optional, as a percent from the entry fill) are checked on each
  bar's high and low. If a bar opens past the level, the fill is at the open (a gap).
  If both levels are hit in one bar, the stop is assumed to fill first (the conservative choice).
- After a stop or target exit, the strategy does not re-enter in the same direction until its
  signal changes. Otherwise it would buy straight back in at the level it just left.
- Margin call: if a position would take the account to zero or below, it is closed at that bar's
  close and the account stops trading. Total return can't go below -100%.
"""
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

ENGINE_VERSION = "2"


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


def _exit_price(direction, entry, stop_pct, target_pct, o, h, l):
    """
    Return (price, reason) if this bar hits a stop or target, otherwise (None, None).
    The price is the level, or the open if the bar gapped past it.
    """
    if direction > 0:
        stop_lvl = entry * (1 - stop_pct) if stop_pct else None
        tgt_lvl = entry * (1 + target_pct) if target_pct else None
        if stop_lvl is not None:
            if o <= stop_lvl:
                return o, "stop"
            if l <= stop_lvl:
                return stop_lvl, "stop"
        if tgt_lvl is not None:
            if o >= tgt_lvl:
                return o, "target"
            if h >= tgt_lvl:
                return tgt_lvl, "target"
    else:
        stop_lvl = entry * (1 + stop_pct) if stop_pct else None
        tgt_lvl = entry * (1 - target_pct) if target_pct else None
        if stop_lvl is not None:
            if o >= stop_lvl:
                return o, "stop"
            if h >= stop_lvl:
                return stop_lvl, "stop"
        if tgt_lvl is not None:
            if o <= tgt_lvl:
                return o, "target"
            if l <= tgt_lvl:
                return tgt_lvl, "target"
    return None, None


def run(df, desired, costs: Costs, position_fraction: float = 1.0,
        stop_pct=None, target_pct=None) -> dict:
    """
    df: bars with open, high, low and close columns.
    desired: the position to hold on each bar, already shifted so it was known before that bar opened.
    stop_pct, target_pct: optional fractions, e.g. 0.02 for 2%.
    Returns {"equity": Series, "trades": list of dicts}.
    """
    idx = df.index
    n = len(df)
    desired = np.asarray(desired).astype(int)
    opens = df["open"].to_numpy(float)
    highs = df["high"].to_numpy(float)
    lows = df["low"].to_numpy(float)
    closes = df["close"].to_numpy(float)
    borrow_per_bar = costs.borrow_rate_annual / bars_per_year(idx)

    cash = costs.starting_cash
    qty = 0
    trade = None
    trades = []
    locked = None      # direction blocked from re-entry after a stop or target
    busted = False     # set after a margin call; no more trading
    equity = np.empty(n)

    def close_trade(time, price, reason):
        nonlocal cash, qty, trade
        d, fill, _ = _fill(-qty, price, costs)
        cash += d
        trade.update(exit_time=time, exit_price=fill, exit_reason=reason,
                     pnl=cash - trade.pop("cash_before"))
        trades.append(trade)
        trade = None
        qty = 0

    for i in range(n):
        if qty < 0:
            cash -= abs(qty) * closes[i] * borrow_per_bar

        want = 0 if busted else int(desired[i])
        if locked is not None and want != locked:
            locked = None

        # Stop-loss and take-profit, checked on this bar's range.
        if qty != 0 and (stop_pct or target_pct):
            px, reason = _exit_price(int(np.sign(qty)), trade["entry_price"],
                                     stop_pct, target_pct, opens[i], highs[i], lows[i])
            if px is not None:
                close_trade(idx[i], px, reason)
                locked = want

        cur = int(np.sign(qty))
        if want != cur and not (qty == 0 and locked == want):
            if qty != 0:
                close_trade(idx[i], opens[i], "signal")
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

        if qty != 0 and cash + qty * closes[i] <= 0:  # margin call
            close_trade(idx[i], closes[i], "margin_call")
            cash = max(cash, 0.0)
            busted = True

        equity[i] = cash + qty * closes[i]

    if qty != 0:  # close anything still open at the end of the data
        close_trade(idx[-1], closes[-1], "end_of_data")
        equity[-1] = cash

    return {"equity": pd.Series(equity, index=idx, name="equity"), "trades": trades}
