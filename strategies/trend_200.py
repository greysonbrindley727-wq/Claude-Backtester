"""200-Day Trend, version 1. Long-only trend filter: in when the price is above its 200-day average, out when below."""
import numpy as np
import pandas as pd

from .base import Strategy


class Trend200(Strategy):
    name = "200-Day Trend"
    version = "1"
    summary = ("Holds the stock while it trades above its 200-day average, "
               "and stays in cash while it trades below.")
    entry_rules = "Long when the close is above the 200-day simple moving average."
    exit_rules = "Sell when the close falls below the 200-day simple moving average."
    timeframe = "1Day"
    weaknesses = ("Slow to get out after a crash and slow to get back in. "
                  "Gets whipsawed when price hovers around the average.")
    changelog = ["1: initial version"]
    default_params = {"period": 200}

    def signals(self, df):
        ma = df["close"].rolling(self.params["period"]).mean()
        values = np.where(df["close"] > ma, 1, 0)   # NaN compares False, so no trades during warm-up
        return pd.Series(values, index=df.index)
