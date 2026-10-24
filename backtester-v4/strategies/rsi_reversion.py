"""RSI Reversion, version 1. Example strategy: replace or add your own in this folder."""
import numpy as np
import pandas as pd

from .base import Strategy


class RsiReversion(Strategy):
    name = "RSI Reversion"
    version = "1"
    summary = ("Buys after RSI shows a stock has fallen too far too fast, and sells once it "
               "recovers to the middle. Shorts the opposite when RSI is stretched high.")
    entry_rules = "Long when RSI(14) closes below 30. Short when RSI(14) closes above 70."
    exit_rules = "Close a long when RSI rises above 50. Close a short when RSI falls below 50."
    timeframe = "1Day"
    weaknesses = ("Strong trends keep RSI pinned high or low, so it can enter early and keep "
                  "losing. Slow to exit after a sharp reversal.")
    changelog = ["1: initial version"]
    default_params = {"period": 14, "buy_below": 30, "short_above": 70, "exit_level": 50}

    def signals(self, df):
        p = self.params
        delta = df["close"].diff()
        gain = delta.clip(lower=0).ewm(alpha=1 / p["period"], adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1 / p["period"], adjust=False).mean()
        rsi = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
        flat = loss == 0
        rsi = rsi.mask(flat, pd.Series(np.where(gain > 0, 100.0, 50.0), index=df.index))
        rsi = rsi.fillna(50.0)

        out = np.zeros(len(df), dtype=int)
        pos = 0
        for i, r in enumerate(rsi.to_numpy()):
            if pos == 0:
                if r < p["buy_below"]:
                    pos = 1
                elif r > p["short_above"]:
                    pos = -1
            elif pos == 1 and r > p["exit_level"]:
                pos = 0
            elif pos == -1 and r < p["exit_level"]:
                pos = 0
            out[i] = pos
        return pd.Series(out, index=df.index)
