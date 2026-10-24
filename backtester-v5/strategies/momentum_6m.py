"""6-Month Momentum, version 1. Trend strategy: long what has risen over about six months, short what has fallen."""
import numpy as np
import pandas as pd

from .base import Strategy


class Momentum6M(Strategy):
    name = "6-Month Momentum"
    version = "1"
    summary = ("Goes long a stock that is higher than it was about six months ago, "
               "and short one that is lower.")
    entry_rules = ("Long when the close is above the close 126 bars (about 6 months) ago. "
                   "Short when it is below.")
    exit_rules = "The position flips when the sign of that comparison changes."
    timeframe = "1Day"
    weaknesses = ("Trend reversals cause repeated losses. Sharp rallies hurt the short side badly.")
    changelog = ["1: initial version"]
    default_params = {"lookback": 126}

    def signals(self, df):
        lb = self.params["lookback"]
        diff = df["close"] - df["close"].shift(lb)
        return np.sign(diff).fillna(0).astype(int)
