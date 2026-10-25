"""Bull Flag Breakout, version 1. Price action: a sharp rise, a tight pause, then a break to new highs."""
import numpy as np
import pandas as pd

from .base import Strategy


class BullFlag(Strategy):
    name = "Bull Flag Breakout"
    version = "1"
    summary = ("After a sharp rise, waits for a tight sideways pause (the flag). "
               "Buys when price breaks above the top of that pause.")
    entry_rules = ("Long when the stock rose over 8% in the 10 bars before the flag, the last 5 bars stayed within 4% "
                   "of price, and the close breaks above the flag's high. Long only.")
    exit_rules = "Sells when the close falls below its 10-day average."
    timeframe = "1Day"
    weaknesses = "Many flags fail and turn into reversals. The pattern is subjective when drawn by hand; this version uses fixed rules."
    changelog = ["1: initial version"]
    default_params = {"pole_bars": 10, "pole_pct": 0.08, "flag_bars": 5, "flag_range": 0.04, "exit_ma": 10}

    def signals(self, df):
        p = self.params
        c, h, l = df["close"], df["high"], df["low"]
        pole = (c.shift(p["flag_bars"]) / c.shift(p["pole_bars"] + p["flag_bars"]) - 1) > p["pole_pct"]
        flag_hi = h.shift(1).rolling(p["flag_bars"]).max()
        flag_lo = l.shift(1).rolling(p["flag_bars"]).min()
        tight = (flag_hi - flag_lo) / c < p["flag_range"]
        breakout = c > flag_hi
        trigger = (pole & tight & breakout).fillna(False).to_numpy()
        exit_ma = c.rolling(p["exit_ma"]).mean().to_numpy()
        close = c.to_numpy()

        out = np.zeros(len(df), dtype=int)
        pos = 0
        for i in range(len(df)):
            if pos == 0 and trigger[i]:
                pos = 1
            elif pos == 1 and close[i] < exit_ma[i]:
                pos = 0
            out[i] = pos
        return pd.Series(out, index=df.index)
