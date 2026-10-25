"""OBV Trend, version 1. Volume: follows On-Balance Volume, a running total that adds volume on up days and subtracts on down days."""
import numpy as np
import pandas as pd

from .base import Strategy
from .indicators import obv


class ObvTrend(Strategy):
    name = "OBV Trend"
    version = "1"
    summary = ("Tracks On-Balance Volume, which adds volume on up days and subtracts it on down days. "
               "When that total is above its 20-day average, the trend is up, and the strategy is long.")
    entry_rules = "Long when OBV is above its 20-day average. Short when it is below."
    exit_rules = "Flips when OBV crosses its average. Always in the market after warm-up."
    timeframe = "1Day"
    weaknesses = ("Uses the IEX volume feed, which is a small share of all trading, so the signal is noisier. "
                  "Price and volume can disagree for long stretches.")
    changelog = ["1: initial version"]
    default_params = {"ma": 20}

    def signals(self, df):
        o = obv(df)
        ma = o.rolling(self.params["ma"]).mean()
        vals = np.where(o > ma, 1, -1)
        vals[ma.isna().to_numpy()] = 0   # no trades until the average exists
        return pd.Series(vals.astype(int), index=df.index)
