"""Supertrend, version 1. Trend: a trailing line based on volatility that flips when price crosses it."""
import numpy as np
import pandas as pd

from .base import Strategy
from .indicators import atr


class Supertrend(Strategy):
    name = "Supertrend"
    version = "1"
    summary = ("Draws a trailing stop line that rises in an uptrend and falls in a downtrend. "
               "Goes long when price is above the line, and short when it is below.")
    entry_rules = "Long while the close is above the Supertrend line. Short while it is below."
    exit_rules = "Flips direction when the close crosses the line. Always in the market."
    timeframe = "1Day"
    weaknesses = "Whipsaws in sideways markets, flipping direction after small moves."
    changelog = ["1: initial version"]
    default_params = {"atr": 10, "mult": 3.0}

    def signals(self, df):
        p = self.params
        hl2 = ((df["high"] + df["low"]) / 2).to_numpy()
        a = atr(df, p["atr"]).to_numpy()
        ub = hl2 + p["mult"] * a
        lb = hl2 - p["mult"] * a
        c = df["close"].to_numpy()
        n = len(df)
        fu = np.full(n, np.nan)
        fl = np.full(n, np.nan)
        trend = np.zeros(n, dtype=int)
        started = False
        t = 0
        for i in range(n):
            if np.isnan(a[i]):
                continue
            if not started:
                fu[i], fl[i] = ub[i], lb[i]
                t = 1
                started = True
            else:
                fu[i] = ub[i] if (ub[i] < fu[i - 1] or c[i - 1] > fu[i - 1]) else fu[i - 1]
                fl[i] = lb[i] if (lb[i] > fl[i - 1] or c[i - 1] < fl[i - 1]) else fl[i - 1]
                if t == 1 and c[i] < fl[i]:
                    t = -1
                elif t == -1 and c[i] > fu[i]:
                    t = 1
            trend[i] = t
        return pd.Series(trend, index=df.index)
