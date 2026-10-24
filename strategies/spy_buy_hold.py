"""SPY Buy and Hold, version 1. Benchmark: buys SPY at the start and holds it."""
import numpy as np
import pandas as pd

from .base import Strategy


class SpyBuyHold(Strategy):
    name = "SPY Buy and Hold"
    version = "1"
    summary = ("Buys SPY on the first day and holds it to the end. "
               "This is the benchmark the other strategies are compared against.")
    entry_rules = "Long on every bar, starting from the first bar."
    exit_rules = "Never sells, except at the end of the test."
    timeframe = "1Day"
    weaknesses = "Takes the full market drop with no protection. Only runs on SPY."
    changelog = ["1: initial version"]
    default_params = {}
    symbols = ["SPY"]

    def signals(self, df):
        return pd.Series(np.ones(len(df), dtype=int), index=df.index)
