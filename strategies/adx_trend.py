"""ADX Trend Strength, version 1. Trend: only trades when the trend is strong enough, and in its direction."""
import numpy as np
import pandas as pd

from .base import Strategy
from .indicators import adx


class AdxTrend(Strategy):
    name = "ADX Trend Strength"
    version = "1"
    summary = ("Measures how strong the trend is (ADX). Only trades when the trend is strong, "
               "long in an uptrend and short in a downtrend, and stays flat when the market has no clear trend.")
    entry_rules = ("Long when ADX is above 25 and the upward direction index (+DI) is above the downward one (-DI). "
                   "Short on the reverse. Flat when ADX is below 25.")
    exit_rules = "Goes flat when ADX falls below 25 or the direction indexes cross."
    timeframe = "1Day"
    weaknesses = "ADX reacts slowly, so it often confirms a trend after much of it is over."
    changelog = ["1: initial version"]
    default_params = {"n": 14, "level": 25}

    def signals(self, df):
        a, pdi, mdi = adx(df, self.params["n"])
        a, pdi, mdi = a.to_numpy(), pdi.to_numpy(), mdi.to_numpy()
        lvl = self.params["level"]
        vals = np.select([(a > lvl) & (pdi > mdi), (a > lvl) & (mdi > pdi)], [1, -1], default=0)
        return pd.Series(vals.astype(int), index=df.index)
