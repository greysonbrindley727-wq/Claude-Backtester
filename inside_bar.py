"""Inside Bar Breakout, version 1. Price action: a quiet bar inside the last bar's range, then a break out of that range."""
import numpy as np
import pandas as pd

from .base import Strategy


class InsideBarBreakout(Strategy):
    name = "Inside Bar Breakout"
    version = "1"
    summary = ("After a bar whose range sits fully inside the bar before it, "
               "buys a break above the bigger bar's high and shorts a break below its low.")
    entry_rules = ("Long when the close breaks above the high of the bar before the inside bar. "
                   "Short when it breaks below that bar's low.")
    exit_rules = "Stays in the last direction until the opposite break happens (always in the market)."
    timeframe = "1Day"
    weaknesses = "Inside bars are common in quiet markets, and breakouts there often fail quickly."
    changelog = ["1: initial version"]
    default_params = {}

    def signals(self, df):
        hi, lo, c = df["high"], df["low"], df["close"]
        inside = (hi < hi.shift(1)) & (lo > lo.shift(1))
        prev_inside = inside.shift(1, fill_value=False).to_numpy()
        mother_hi = hi.shift(2).to_numpy()
        mother_lo = lo.shift(2).to_numpy()
        close = c.to_numpy()

        out = np.zeros(len(df), dtype=int)
        pos = 0
        for i in range(len(df)):
            if prev_inside[i]:
                if close[i] > mother_hi[i]:
                    pos = 1
                elif close[i] < mother_lo[i]:
                    pos = -1
            out[i] = pos
        return pd.Series(out, index=df.index)
