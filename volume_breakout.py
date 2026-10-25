"""Volume Breakout, version 1. Volume: buys a 20-day high only when it comes with unusually heavy trading."""
import numpy as np
import pandas as pd

from .base import Strategy


class VolumeBreakout(Strategy):
    name = "Volume Breakout"
    version = "1"
    summary = ("Buys when price breaks above its 20-day high on volume at least 1.5 times normal. "
               "Heavy volume suggests real buying interest, not just drift.")
    entry_rules = ("Long when the close is above the highest high of the last 20 bars, "
                   "and today's volume is over 1.5 times the 20-day average. Long only.")
    exit_rules = "Sells when the close falls below the lowest low of the last 10 bars."
    timeframe = "1Day"
    weaknesses = ("Volume data here comes from the IEX feed only, which is a small share of all trading, "
                  "so the volume signal is noisier than it would be with full market volume.")
    changelog = ["1: initial version"]
    default_params = {"entry": 20, "exit": 10, "vol_mult": 1.5}

    def signals(self, df):
        p = self.params
        hi = df["high"].shift(1).rolling(p["entry"]).max().to_numpy()
        lo = df["low"].shift(1).rolling(p["exit"]).min().to_numpy()
        vavg = df["volume"].shift(1).rolling(p["entry"]).mean().to_numpy()
        c = df["close"].to_numpy()
        v = df["volume"].to_numpy()

        out = np.zeros(len(df), dtype=int)
        pos = 0
        for i in range(len(df)):
            if pos == 0 and c[i] > hi[i] and v[i] > p["vol_mult"] * vavg[i]:
                pos = 1
            elif pos == 1 and c[i] < lo[i]:
                pos = 0
            out[i] = pos
        return pd.Series(out, index=df.index)
