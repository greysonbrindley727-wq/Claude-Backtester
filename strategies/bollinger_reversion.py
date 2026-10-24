"""Bollinger Reversion, version 1. Mean reversion: buys sharp drops below the band, sells at the average."""
import numpy as np
import pandas as pd

from .base import Strategy


class BollingerReversion(Strategy):
    name = "Bollinger Reversion"
    version = "1"
    summary = ("Buys when a stock drops well below its recent average, "
               "and sells once it climbs back to that average.")
    entry_rules = ("Long when the close falls below the 20-day average minus 2 standard deviations. "
                   "Long only.")
    exit_rules = ("Sell when the close rises back above the 20-day average. "
                  "Also sells at a 5% stop-loss below the entry price.")
    timeframe = "1Day"
    stop_pct = 0.05
    weaknesses = ("In a steady downtrend, price keeps falling below the band. "
                  "The stop limits the loss but also cuts some recoveries short.")
    changelog = ["1: initial version"]
    default_params = {"period": 20, "num_std": 2.0}

    def signals(self, df):
        p = self.params
        close = df["close"]
        mid = close.rolling(p["period"]).mean().to_numpy()
        sd = close.rolling(p["period"]).std(ddof=0).to_numpy()
        lower = mid - p["num_std"] * sd
        c = close.to_numpy()

        out = np.zeros(len(df), dtype=int)
        pos = 0
        for i in range(len(df)):
            if pos == 0 and c[i] < lower[i]:
                pos = 1
            elif pos == 1 and c[i] > mid[i]:
                pos = 0
            out[i] = pos
        return pd.Series(out, index=df.index)
