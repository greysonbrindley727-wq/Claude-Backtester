"""Williams %R Revert, version 1. Mean reversion: buys when the close sits at the bottom of its 14-day range."""
import numpy as np
import pandas as pd

from .base import Strategy
from .indicators import williams_r


class WilliamsRevert(Strategy):
    name = "Williams %R Revert"
    version = "1"
    summary = ("Measures where the close sits in its 14-day range. When it is near the bottom, buys, "
               "and sells once it climbs back to the middle.")
    entry_rules = "Long when Williams %R is below -90 (close near the bottom of the 14-day range). Long only."
    exit_rules = "Sells when %R rises above -50. Also sells at a 4% stop-loss."
    timeframe = "1Day"
    stop_pct = 0.04
    weaknesses = "A stock in a strong downtrend stays at the bottom of its range, and the strategy keeps buying into the fall."
    changelog = ["1: initial version"]
    default_params = {"n": 14, "entry": -90, "exit": -50}

    def signals(self, df):
        w = williams_r(df, self.params["n"]).to_numpy()
        out = np.zeros(len(df), dtype=int)
        pos = 0
        for i in range(len(df)):
            if pos == 0 and w[i] < self.params["entry"]:
                pos = 1
            elif pos == 1 and w[i] > self.params["exit"]:
                pos = 0
            out[i] = pos
        return pd.Series(out, index=df.index)
