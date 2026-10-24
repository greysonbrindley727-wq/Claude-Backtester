# Backtester

Runs many trading strategies over historical prices, with costs, and ranks them.
Winners get reviewed, then copied into the paper-trading bot's `strategies/` folder.

## Files and versions

| File | Version | What it does |
|---|---|---|
| `run_backtests.py` | 1 | Runs everything and writes the results files |
| `engine.py` | 1 | Simulates trades: fills at next open, slippage, fees, borrow costs |
| `metrics.py` | 1 | Return, drawdown, Sharpe, win rate, profit factor, monthly stats |
| `data.py` | 1 | Loads bars from `data/` or downloads them once from Alpaca |
| `strategies/base.py` | 1 | The interface every strategy follows |
| `strategies/ema_cross.py` | 1 | Example strategy: EMA Cross |
| `strategies/rsi_reversion.py` | 1 | Example strategy: RSI Reversion |
| `strategies/__init__.py` | 1 | Registry: add new strategies here |
| `config.json` | 1 | Symbols, dates, holdout split, cost settings |

## Adding a strategy

1. Create `strategies/your_name.py`. Subclass `Strategy` and fill in the description fields
   (name, summary, entry and exit rules, weaknesses, changelog).
2. Write `signals(df)`. It returns 1 (long), -1 (short), or 0 (flat) for each bar, and may only
   use data up to that bar.
3. Import it in `strategies/__init__.py` and add it to `ALL_STRATEGIES`.

## Results

Each run writes three files to `results/`, named by date:

- `leaderboard-<date>.csv`: one row per strategy. Sort by any column.
- `details-<date>.csv`: one row per strategy, stock and period.
- `backtest-<date>.json`: everything, including equity curves and every trade.

Out-of-sample columns come from the last 30% of history, which the screen never saw.
A large `overfit_gap_pct` (in-sample return minus out-of-sample return) is a warning sign.

## Known limits (version 1)

- Daily bars only in the example config. Intraday works, but the runner is not tuned for speed on years of 1-minute data.
- Stop-loss and take-profit are not modeled yet.
- Fees use the rates in `config.json`. Check them against current SEC and FINRA published rates.
- Results on the sample data in testing are fake, because they come from random numbers. Only real market data gives meaningful results.
