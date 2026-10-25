"""Stochastic Cross, version 1. Momentum: buys oversold line crosses and shorts overbought ones."""
import numpy as np
import pandas as pd

from .base import Strategy
from .indicators import stochastic


class StochasticCross(Strategy):
    name = "Stochastic Cross"
    version = "1"
    summary = ("Watches where the close sits within its 14-day range. Buys when the fast line crosses "
               "above the slow line from oversold territory, and shorts the reverse from overbought.")
    entry_rules = ("Long when %K crosses above %D while %K is below 30. "
                   "Short when %K crosses below %D while %K is above 70.")
    exit_rules = "Closes when the lines cross back the other way."
    timeframe = "1Day"
    weaknesses = "In a strong trend, the stock stays overbought or oversold for a long time and signals fire too early."
    changelog = ["1: initial version"]
    default_params = {"k": 14, "d": 3, "low": 30, "high": 70}

    def signals(self, df):
        p = self.params
        K, D = stochastic(df, p["k"], p["d"])
        k, d = K.to_numpy(), D.to_numpy()
        k_prev = K.shift(1).to_numpy()
        d_prev = D.shift(1).to_numpy()
        up = (k > d) & (k_prev <= d_prev)
        dn = (k < d) & (k_prev >= d_prev)

        out = np.zeros(len(df), dtype=int)
        pos = 0
        for i in range(len(df)):
            if pos == 0:
                if up[i] and k[i] < p["low"]:
                    pos = 1
                elif dn[i] and k[i] > p["high"]:
                    pos = -1
            elif pos == 1 and dn[i]:
                pos = 0
            elif pos == -1 and up[i]:
                pos = 0
            out[i] = pos
        return pd.Series(out, index=df.index)
