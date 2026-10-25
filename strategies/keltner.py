"""Keltner Channel Breakout, version 1. Trend: trades breaks of a volatility-based channel around a moving average."""
import numpy as np
import pandas as pd

from .base import Strategy
from .indicators import atr, ema


class KeltnerBreakout(Strategy):
    name = "Keltner Channel Breakout"
    version = "1"
    summary = ("Draws a channel two average true ranges above and below a 20-day average. "
               "Buys when price closes above the top band, shorts below the bottom band.")
    entry_rules = "Long when the close is above the 20-day average plus 2 ATR. Short when below the average minus 2 ATR."
    exit_rules = "Closes when price crosses back through the 20-day average."
    timeframe = "1Day"
    weaknesses = "Breakouts that happen during a volatility spike reverse quickly. Chops in sideways markets."
    changelog = ["1: initial version"]
    default_params = {"ma": 20, "atr": 10, "mult": 2.0}

    def signals(self, df):
        p = self.params
        mid = ema(df["close"], p["ma"])
        band = p["mult"] * atr(df, p["atr"])
        upper = (mid + band).to_numpy()
        lower = (mid - band).to_numpy()
        mid_np = mid.to_numpy()
        close = df["close"].to_numpy()

        out = np.zeros(len(df), dtype=int)
        pos = 0
        for i in range(len(df)):
            if pos == 0:
                if close[i] > upper[i]:
                    pos = 1
                elif close[i] < lower[i]:
                    pos = -1
            elif pos == 1 and close[i] < mid_np[i]:
                pos = 0
            elif pos == -1 and close[i] > mid_np[i]:
                pos = 0
            out[i] = pos
        return pd.Series(out, index=df.index)
