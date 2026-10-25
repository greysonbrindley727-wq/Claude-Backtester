"""Regression Channel Breakout, version 1. Trendlines: fits a straight line through recent prices and trades breaks of its channel."""
import numpy as np
import pandas as pd

from .base import Strategy
from .indicators import rolling_linreg


class RegressionChannel(Strategy):
    name = "Regression Channel Breakout"
    version = "1"
    summary = ("Fits a trendline through the last 50 days. When the trend is up and price breaks above "
               "the top of the channel, buys. When the trend is down and price breaks below the bottom, shorts.")
    entry_rules = ("Long when the 50-day trend slope is up and the close is above the channel top "
                   "(trendline plus 2 standard deviations). Short on the reverse.")
    exit_rules = "Closes when price crosses back through the middle trendline."
    timeframe = "1Day"
    weaknesses = "Channels get redrawn as new bars come in, so breakouts can appear and disappear. Fails in flat markets."
    changelog = ["1: initial version"]
    default_params = {"length": 50, "width": 2.0}

    def signals(self, df):
        close = df["close"].to_numpy()
        fit, slope, sd = rolling_linreg(close, self.params["length"])
        upper = fit + self.params["width"] * sd
        lower = fit - self.params["width"] * sd

        out = np.zeros(len(df), dtype=int)
        pos = 0
        for i in range(len(df)):
            if pos == 0:
                if slope[i] > 0 and close[i] > upper[i]:
                    pos = 1
                elif slope[i] < 0 and close[i] < lower[i]:
                    pos = -1
            elif pos == 1 and close[i] < fit[i]:
                pos = 0
            elif pos == -1 and close[i] > fit[i]:
                pos = 0
            out[i] = pos
        return pd.Series(out, index=df.index)
