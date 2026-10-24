"""
Strategy registry. To add a strategy: create its file here, import the class,
and add it to ALL_STRATEGIES.
"""
from .ema_cross import EmaCross
from .rsi_reversion import RsiReversion

ALL_STRATEGIES = [
    EmaCross,
    RsiReversion,
]
