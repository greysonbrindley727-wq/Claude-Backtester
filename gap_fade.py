"""Gap Fade, version 1. Price action: buys a big gap down, expecting it to fill back toward the prior close."""
import numpy as np
import pandas as pd

from .base import Strategy


class GapFade(Strategy):
    name = "Gap Fade"
    version = "1"
    summary = ("When a stock opens more than 1% below the previous close, buys and waits for the gap to fill.")
    entry_rules = "Long at the close of a day that opened more than 1% below the prior close. Long only."
    exit_rules = "Sells once the close reaches the prior close (gap filled), or after 3 bars."
    timeframe = "1Day"
    weaknesses = "Gaps that come from bad news often keep falling. The gap may never fill."
    changelog = ["1: initial version"]
    default_params = {"gap_pct": 0.01, "max_hold": 3}

    def signals(self, df):
        o = df["open"].to_numpy()
        c = df["close"].to_numpy()
        prev_c = df["close"].shift(1).to_numpy()
        gap = o / prev_c - 1

        out = np.zeros(len(df), dtype=int)
        pos, held, target = 0, 0, np.nan
        for i in range(len(df)):
            if pos == 1:
                held += 1
                if c[i] >= target or held >= self.params["max_hold"]:
                    pos = 0
            if pos == 0 and gap[i] < -self.params["gap_pct"]:
                pos, held, target = 1, 0, prev_c[i]
            out[i] = pos
        return pd.Series(out, index=df.index)
