"""Donchian Breakout, version 1. Trend strategy: buys new highs, sells new lows, goes short on the reverse."""
import numpy as np
import pandas as pd

from .base import Strategy


class Donchian(Strategy):
    name = "Donchian Breakout"
    version = "1"
    summary = ("Buys when price breaks above its highest high of the last 20 days, "
               "and goes short when it breaks below the lowest low.")
    entry_rules = ("Long when the close is above the highest high of the previous 20 bars. "
                   "Short when the close is below the lowest low of the previous 20 bars.")
    exit_rules = ("Close a long when the close drops below the lowest low of the previous 10 bars. "
                  "Close a short when the close rises above the highest high of the previous 10 bars.")
    timeframe = "1Day"
    weaknesses = "Sideways markets trigger false breakouts and repeated small losses."
    changelog = ["1: initial version"]
    default_params = {"entry": 20, "exit": 10}

    def signals(self, df):
        p = self.params
        hi_in = df["high"].shift(1).rolling(p["entry"]).max().to_numpy()
        lo_in = df["low"].shift(1).rolling(p["entry"]).min().to_numpy()
        hi_out = df["high"].shift(1).rolling(p["exit"]).max().to_numpy()
        lo_out = df["low"].shift(1).rolling(p["exit"]).min().to_numpy()
        close = df["close"].to_numpy()

        out = np.zeros(len(df), dtype=int)
        pos = 0
        for i in range(len(df)):
            if pos == 0:
                if close[i] > hi_in[i]:
                    pos = 1
                elif close[i] < lo_in[i]:
                    pos = -1
            elif pos == 1 and close[i] < lo_out[i]:
                pos = 0
            elif pos == -1 and close[i] > hi_out[i]:
                pos = 0
            out[i] = pos
        return pd.Series(out, index=df.index)
