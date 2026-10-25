"""MACD Crossover, version 1. Momentum: trades when the MACD line crosses its signal line."""
import numpy as np
import pandas as pd

from .base import Strategy
from .indicators import macd


class MacdCross(Strategy):
    name = "MACD Crossover"
    version = "1"
    summary = ("Buys when the fast momentum line (MACD) crosses above its smoothed signal line, "
               "and shorts when it crosses below.")
    entry_rules = "Long while MACD is above its 9-day signal line. Short while it is below. (12, 26, 9 settings.)"
    exit_rules = "Flips when the lines cross. Always in the market."
    timeframe = "1Day"
    weaknesses = "Late signals: most of the move is over by the time the lines cross. Whipsaws in ranges."
    changelog = ["1: initial version"]
    default_params = {"fast": 12, "slow": 26, "signal": 9}

    def signals(self, df):
        p = self.params
        line, sig = macd(df["close"], p["fast"], p["slow"], p["signal"])
        vals = np.sign((line - sig).to_numpy())
        vals = np.nan_to_num(vals).astype(int)
        return pd.Series(vals, index=df.index)
