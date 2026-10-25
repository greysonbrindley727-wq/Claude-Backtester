"""Low-Volatility Trend, version 1. Calm-market trend: holds only when the stock is in an uptrend and calmer than usual."""
import pandas as pd

from .base import Strategy


class LowVolTrend(Strategy):
    name = "Low-Volatility Trend"
    version = "1"
    summary = ("Holds a stock only when it is above its 100-day average and its recent daily swings "
               "are calmer than its typical level over the past year. Stays in cash otherwise.")
    entry_rules = ("Long when the close is above the 100-day average and the 60-day volatility is below its "
                   "one-year median. Long only.")
    exit_rules = "Sells when either condition stops being true. Holds only in calm uptrends."
    timeframe = "1Day"
    weaknesses = ("Sits out a lot of the time, so it can miss strong moves. Calm markets can turn into fast crashes, "
                  "and the strategy may be slow to get out.")
    changelog = ["1: initial version"]
    default_params = {"vol_window": 60, "median_window": 252, "trend_window": 100}

    def signals(self, df):
        p = self.params
        close = df["close"]
        vol = close.pct_change().rolling(p["vol_window"]).std()
        typical = vol.rolling(p["median_window"]).median()
        uptrend = close > close.rolling(p["trend_window"]).mean()
        on = (vol < typical) & uptrend
        return on.fillna(False).astype(int)
