"""EMA Cross, version 1. Example strategy: replace or add your own in this folder."""
import numpy as np
import pandas as pd

from .base import Strategy


class EmaCross(Strategy):
    name = "EMA Cross"
    version = "1"
    summary = ("Goes long when a fast moving average rises above a slow one, "
               "and short when it falls below.")
    entry_rules = "Long when EMA(9) is above EMA(21). Short when EMA(9) is below EMA(21)."
    exit_rules = "The position flips when the averages cross back."
    timeframe = "1Day"
    weaknesses = "Whipsaws in sideways markets. Lags after sharp moves."
    changelog = ["1: initial version"]
    default_params = {"fast": 9, "slow": 21}

    def signals(self, df):
        fast = df["close"].ewm(span=self.params["fast"], adjust=False).mean()
        slow = df["close"].ewm(span=self.params["slow"], adjust=False).mean()
        values = np.where(fast > slow, 1, np.where(fast < slow, -1, 0))
        return pd.Series(values, index=df.index)
