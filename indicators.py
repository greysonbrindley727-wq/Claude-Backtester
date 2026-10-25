"""
Shared indicator helpers, version 1.
Every helper only uses the current bar and earlier bars, so it is safe to backtest.
"""
import numpy as np
import pandas as pd


def true_range(df):
    prev = df["close"].shift(1)
    return pd.concat([df["high"] - df["low"],
                      (df["high"] - prev).abs(),
                      (df["low"] - prev).abs()], axis=1).max(axis=1)


def atr(df, n=14):
    return true_range(df).rolling(n).mean()


def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def macd(close, fast=12, slow=26, signal=9):
    line = ema(close, fast) - ema(close, slow)
    return line, ema(line, signal)


def obv(df):
    direction = np.sign(df["close"].diff()).fillna(0)
    return (direction * df["volume"]).cumsum()


def stochastic(df, k=14, d=3):
    lo = df["low"].rolling(k).min()
    hi = df["high"].rolling(k).max()
    pct_k = 100 * (df["close"] - lo) / (hi - lo)
    return pct_k, pct_k.rolling(d).mean()


def williams_r(df, n=14):
    lo = df["low"].rolling(n).min()
    hi = df["high"].rolling(n).max()
    return -100 * (hi - df["close"]) / (hi - lo)


def adx(df, n=14):
    up = df["high"].diff()
    down = -df["low"].diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=df.index)
    tr = true_range(df).ewm(alpha=1 / n, adjust=False).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / n, adjust=False).mean() / tr
    minus_di = 100 * minus_dm.ewm(alpha=1 / n, adjust=False).mean() / tr
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    return dx.ewm(alpha=1 / n, adjust=False).mean(), plus_di, minus_di


def rolling_linreg(y, n):
    """Straight-line fit over the last n bars. Returns (value at the last bar, slope, residual std)."""
    x = np.arange(n, dtype=float)
    xm = x.mean()
    sxx = ((x - xm) ** 2).sum()
    fit = np.full(len(y), np.nan)
    slope = np.full(len(y), np.nan)
    sd = np.full(len(y), np.nan)
    for i in range(n - 1, len(y)):
        seg = y[i - n + 1: i + 1]
        ym = seg.mean()
        b = ((x - xm) * (seg - ym)).sum() / sxx
        line = (ym - b * xm) + b * x
        fit[i], slope[i], sd[i] = line[-1], b, (seg - line).std()
    return fit, slope, sd
