"""
Strategy interface, version 1.

Every strategy file follows this shape. The description fields feed the
dashboard's strategy card, so fill them in when you add a strategy.
"""
import pandas as pd


class Strategy:
    name = "Unnamed strategy"
    version = "1"
    summary = ""              # one or two plain-English sentences
    entry_rules = ""
    exit_rules = ""
    timeframe = "1Day"
    weaknesses = ""           # fill in as you learn from results
    changelog = []
    default_params = {}
    position_fraction = 1.0   # share of cash used per trade (1.0 = full account)

    def __init__(self, **overrides):
        self.params = {**self.default_params, **overrides}

    def signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Return a Series aligned to df.index with values 1 (long), -1 (short) or 0 (flat).

        The value at bar i is the position you want at the CLOSE of bar i.
        It may only use bars 0..i. The engine fills it at bar i+1's open.
        """
        raise NotImplementedError

    def describe(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "summary": self.summary,
            "entry_rules": self.entry_rules,
            "exit_rules": self.exit_rules,
            "timeframe": self.timeframe,
            "params": self.params,
            "position_fraction": self.position_fraction,
            "weaknesses": self.weaknesses,
            "changelog": self.changelog,
        }
