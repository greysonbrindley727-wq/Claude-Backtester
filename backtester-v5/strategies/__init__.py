"""
Strategy registry. To add a strategy: create its file here, import the class,
and add it to ALL_STRATEGIES.
"""
from .bollinger_reversion import BollingerReversion
from .donchian import Donchian
from .ema_cross import EmaCross
from .momentum_6m import Momentum6M
from .rsi2_pullback import Rsi2Pullback
from .rsi_reversion import RsiReversion
from .spy_buy_hold import SpyBuyHold
from .trend_200 import Trend200

ALL_STRATEGIES = [
    SpyBuyHold,
    EmaCross,
    RsiReversion,
    Donchian,
    Trend200,
    BollingerReversion,
    Momentum6M,
    Rsi2Pullback,
]
