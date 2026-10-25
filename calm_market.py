"""Calm Market Hold, version 1. Low-volatility holding: holds when short-term volatility is in its calmest 40% of the past year."""
import pandas as pd

from .base import Strategy


class CalmMarketHold(Strategy):
    name = "Calm Market Hold"
    version = "1"
    summary = ("Holds a stock only while its recent volatility is among the calmest 40% of the past year "
               "and it is above its 50-day average. Stays in cash otherwise.")
    entry_rules = ("Long when the 20-day volatility is at or below its 40th percentile over the past year "
                   "and the close is above the 50-day average. Long only.")
    exit_rules = "Sells when either condition stops being true."
    timeframe = "1Day"
    weaknesses = ("Calm periods often end with a sudden spike in volatility, and this strategy only reacts after it starts. "
                  "Sits out many rallies.")
    changelog = ["1: initial version"]
    default_params = {"vol_window": 20, "lookback": 252, "pct": 0.4, "trend_window": 50}

    def signals(self, df):
        p = self.params
        close = df["close"]
        vol = close.pct_change().rolling(p["vol_window"]).std()
        cutoff = vol.rolling(p["lookback"]).quantile(p["pct"])
        uptrend = close > close.rolling(p["trend_window"]).mean()
        on = (vol <= cutoff) & uptrend
        return on.fillna(False).astype(int)
