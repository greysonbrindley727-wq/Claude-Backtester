"""Pin Bar Reversal, version 1. Price action: a candle with a long rejection wick, traded in the direction of the rejection."""
import numpy as np
import pandas as pd

from .base import Strategy


class PinBarReversal(Strategy):
    name = "Pin Bar Reversal"
    version = "1"
    summary = ("Buys when a candle has a long lower wick and closes near its high, "
               "showing buyers pushed the price back up. Shorts the mirror image.")
    entry_rules = ("Long when the lower wick is at least twice the body and the close is in the top third of the bar. "
                   "Short when the upper wick is at least twice the body and the close is in the bottom third.")
    exit_rules = "Sells after 3 bars, or when the position is flat. Holds for a fixed time."
    timeframe = "1Day"
    weaknesses = "Rejection wicks are common on volatile days with no real reversal behind them."
    changelog = ["1: initial version"]
    default_params = {"hold_bars": 3}

    def signals(self, df):
        o, h, l, c = (df[k].to_numpy() for k in ("open", "high", "low", "close"))
        body = np.abs(c - o)
        top = np.maximum(o, c)
        bottom = np.minimum(o, c)
        rng = h - l
        upper_wick = h - top
        lower_wick = bottom - l
        with np.errstate(invalid="ignore", divide="ignore"):
            bull = (rng > 0) & (lower_wick > 2 * body) & (c > l + 0.66 * rng)
            bear = (rng > 0) & (upper_wick > 2 * body) & (c < l + 0.33 * rng)

        out = np.zeros(len(df), dtype=int)
        pos, held = 0, 0
        for i in range(len(df)):
            if pos != 0:
                held += 1
                if held >= self.params["hold_bars"]:
                    pos = 0
            if pos == 0:
                if bull[i]:
                    pos, held = 1, 0
                elif bear[i]:
                    pos, held = -1, 0
            out[i] = pos
        return pd.Series(out, index=df.index)
