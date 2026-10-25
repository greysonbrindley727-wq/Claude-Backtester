"""
Strategy registry. To add a strategy: create its file here, import the class,
and add it to ALL_STRATEGIES.
"""
from .adx_trend import AdxTrend
from .bollinger_reversion import BollingerReversion
from .bull_flag import BullFlag
from .calm_market import CalmMarketHold
from .donchian import Donchian
from .ema_cross import EmaCross
from .engulfing import EngulfingReversal
from .gap_fade import GapFade
from .inside_bar import InsideBarBreakout
from .keltner import KeltnerBreakout
from .low_vol_trend import LowVolTrend
from .macd_cross import MacdCross
from .momentum_6m import Momentum6M
from .obv_trend import ObvTrend
from .pin_bar import PinBarReversal
from .regression_channel import RegressionChannel
from .rsi2_pullback import Rsi2Pullback
from .rsi_reversion import RsiReversion
from .spy_buy_hold import SpyBuyHold
from .stochastic_cross import StochasticCross
from .supertrend import Supertrend
from .trend_200 import Trend200
from .volume_breakout import VolumeBreakout
from .volume_climax import VolumeClimaxBounce
from .williams_r import WilliamsRevert

ALL_STRATEGIES = [
    SpyBuyHold,
    EmaCross,
    RsiReversion,
    Donchian,
    Trend200,
    BollingerReversion,
    Momentum6M,
    Rsi2Pullback,
    InsideBarBreakout,
    EngulfingReversal,
    PinBarReversal,
    GapFade,
    RegressionChannel,
    KeltnerBreakout,
    Supertrend,
    MacdCross,
    VolumeBreakout,
    ObvTrend,
    VolumeClimaxBounce,
    StochasticCross,
    WilliamsRevert,
    AdxTrend,
    LowVolTrend,
    CalmMarketHold,
    BullFlag,
]
