"""Engulfing Reversal, version 1. Price action: a candle that fully swallows the candle before it, in the other direction."""
import numpy as np
import pandas as pd

from .base import Strategy


class EngulfingReversal(Strategy):
    name = "Engulfing Reversal"
    version = "1"
    summary = ("Buys after a bullish candle swallows the body of the bearish candle before it, "
               "and shorts after the reverse pattern.")
    entry_rules = ("Long on a bullish engulfing candle: green body covers the previous red body. "
                   "Short on a bearish engulfing candle.")
    exit_rules = "Reverses on the opposite pattern. Also sells at a 3% stop-loss."
    timeframe = "1Day"
    stop_pct = 0.03
    weaknesses = "Engulfing candles happen often in choppy markets, and many reversals don't hold."
    changelog = ["1: initial version"]
    default_params = {}

    def signals(self, df):
        o, c = df["open"], df["close"]
        bull = (c > o) & (c.shift(1) < o.shift(1)) & (c > o.shift(1)) & (o < c.shift(1))
        bear = (c < o) & (c.shift(1) > o.shift(1)) & (c < o.shift(1)) & (o > c.shift(1))
        bull = bull.fillna(False).to_numpy()
        bear = bear.fillna(False).to_numpy()

        out = np.zeros(len(df), dtype=int)
        pos = 0
        for i in range(len(df)):
            if bull[i]:
                pos = 1
            elif bear[i]:
                pos = -1
            out[i] = pos
        return pd.Series(out, index=df.index)
