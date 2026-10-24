"""
Data loading, version 1.

Reads bars from data/<SYMBOL>_<TIMEFRAME>.csv. If a file is missing and Alpaca keys are
set in the environment (APCA_API_KEY_ID, APCA_API_SECRET_KEY), it downloads the bars once,
saves them to that file, and reuses the file on later runs.
"""
import json
import os
import urllib.parse
import urllib.request

import pandas as pd

DATA_VERSION = "1"
ALPACA_BASE = "https://data.alpaca.markets"
COLUMNS = ["open", "high", "low", "close", "volume"]


def load_csv(path):
    raw = pd.read_csv(path)
    ts = pd.to_datetime(raw["timestamp"], utc=True)
    df = raw[COLUMNS].astype(float)
    df.index = pd.DatetimeIndex(ts, name="timestamp")
    return df.dropna(subset=["close"]).sort_index()


def fetch_alpaca(symbol, timeframe, start, end, key, secret, feed="iex"):
    """Download bars from Alpaca's market data API, following pagination. Split/dividend adjusted."""
    rows = []
    token = None
    while True:
        params = {"timeframe": timeframe, "start": start, "end": end,
                  "limit": 10000, "adjustment": "all", "feed": feed}
        if token:
            params["page_token"] = token
        url = f"{ALPACA_BASE}/v2/stocks/{symbol}/bars?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"APCA-API-KEY-ID": key,
                                                   "APCA-API-SECRET-KEY": secret})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        rows += data.get("bars") or []
        token = data.get("next_page_token")
        if not token:
            break
    if not rows:
        raise ValueError(f"Alpaca returned no bars for {symbol} {timeframe} {start}..{end}")
    df = pd.DataFrame(rows).rename(columns={"t": "timestamp", "o": "open", "h": "high",
                                            "l": "low", "c": "close", "v": "volume"})
    return df[["timestamp"] + COLUMNS]


def load_bars(symbol, timeframe, start, end, data_dir):
    path = os.path.join(data_dir, f"{symbol}_{timeframe}.csv")
    if not os.path.exists(path):
        key = os.environ.get("APCA_API_KEY_ID")
        secret = os.environ.get("APCA_API_SECRET_KEY")
        if not (key and secret):
            raise FileNotFoundError(f"No data file at {path}, and Alpaca keys are not set.")
        raw = fetch_alpaca(symbol, timeframe, f"{start}T00:00:00Z", f"{end}T23:59:59Z",
                           key, secret)
        os.makedirs(data_dir, exist_ok=True)
        raw.to_csv(path, index=False)
    df = load_csv(path)
    lo = pd.Timestamp(start, tz="UTC")
    hi = pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1)
    return df[(df.index >= lo) & (df.index < hi)]
