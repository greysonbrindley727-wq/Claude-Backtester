"""Volume Climax Bounce, version 1. Volume: buys a panic sell-off on heavy volume once the bar closes off its lows."""
import numpy as np
import pandas as pd

from .base import Strategy


class VolumeClimaxBounce(Strategy):
    name = "Volume Climax Bounce"
    version = "1"
    summary = ("When a down day comes with panic volume and the close recovers into the upper half "
               "of the day's range, buys the bounce and holds for a few days.")
    entry_rules = ("Long on a day that closes lower than the day before, on volume at least 2 times the 20-day average, "
                   "with the close in the top half of the day's range.")
    exit_rules = "Sells after 3 bars. Long only."
    timeframe = "1Day"
    weaknesses = ("A panic day can be the start of a longer crash. Also uses IEX volume, which is noisier "
                  "than full market volume.")
    changelog = ["1: initial version"]
    default_params = {"vol_mult": 2.0, "hold_bars": 3}

    def signals(self, df):
        c = df["close"]
        h, l = df["high"], df["low"]
        v = df["volume"]
        vavg = v.shift(1).rolling(20).mean()
        rng = (h - l)
        trigger = ((c < c.shift(1)) & (v > self.params["vol_mult"] * vavg)
                   & (rng > 0) & ((c - l) / rng > 0.5)).fillna(False).to_numpy()

        out = np.zeros(len(df), dtype=int)
        pos, held = 0, 0
        for i in range(len(df)):
            if pos == 1:
                held += 1
                if held >= self.params["hold_bars"]:
                    pos = 0
            if pos == 0 and trigger[i]:
                pos, held = 1, 0
            out[i] = pos
        return pd.Series(out, index=df.index)
