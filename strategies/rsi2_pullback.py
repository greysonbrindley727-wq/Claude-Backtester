"""RSI(2) Pullback, version 1. Buys short dips inside an uptrend and sells on the quick bounce."""
import numpy as np
import pandas as pd

from .base import Strategy


def _rsi(close, period):
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(50.0)


class Rsi2Pullback(Strategy):
    name = "RSI(2) Pullback"
    version = "1"
    summary = ("Buys a short dip in an uptrend, once the stock is very oversold for a day or two, "
               "and sells on the bounce.")
    entry_rules = ("Long when the close is above the 200-day average and the 2-day RSI is below 10. "
                   "Long only.")
    exit_rules = "Sell when the close is above the 5-day average."
    timeframe = "1Day"
    weaknesses = ("Pullbacks in a bear market can turn into long declines. "
                  "Works best on stocks that bounce quickly.")
    changelog = ["1: initial version"]
    default_params = {"trend": 200, "rsi_period": 2, "entry_below": 10, "exit_ma": 5}

    def signals(self, df):
        p = self.params
        close = df["close"]
        trend = close.rolling(p["trend"]).mean().to_numpy()
        exit_ma = close.rolling(p["exit_ma"]).mean().to_numpy()
        rsi = _rsi(close, p["rsi_period"]).to_numpy()
        c = close.to_numpy()

        out = np.zeros(len(df), dtype=int)
        pos = 0
        for i in range(len(df)):
            if pos == 0 and c[i] > trend[i] and rsi[i] < p["entry_below"]:
                pos = 1
            elif pos == 1 and c[i] > exit_ma[i]:
                pos = 0
            out[i] = pos
        return pd.Series(out, index=df.index)
