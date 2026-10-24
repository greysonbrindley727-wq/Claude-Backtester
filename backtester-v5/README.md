# Backtester

Runs many trading strategies over historical prices, with costs, and ranks them.
Winners get reviewed, then copied into the paper-trading bot's `strategies/` folder.

## Files and versions

| File | Version | What it does |
|---|---|---|
| `run_backtests.py` | 1 | Runs everything and writes the results files |
| `engine.py` | 2 | Simulates trades: fills at next open, slippage, fees, borrow costs |
| `metrics.py` | 1 | Return, drawdown, Sharpe, win rate, profit factor, monthly stats |
| `data.py` | 1 | Loads bars from `data/` or downloads them once from Alpaca |
| `strategies/base.py` | 1 | The interface every strategy follows |
| `strategies/ema_cross.py` | 1 | Example strategy: EMA Cross |
| `strategies/rsi_reversion.py` | 1 | Example strategy: RSI Reversion |
| `strategies/__init__.py` | 1 | Registry: add new strategies here |
| `config.json` | 1 | Symbols, dates, holdout split, cost settings |
| `requirements.txt` | 1 | Python packages for GitHub Actions |
| `.github/workflows/backtest.yml` | 1 | Runs the backtester on GitHub when you click Run |

## Running it on GitHub

1. In the repo, go to Settings, then Secrets and variables, then Actions. Add two secrets: `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY`, using your Alpaca paper account's data keys.
2. Go to the Actions tab, choose "Backtest", and click "Run workflow".
3. When it finishes, download the `backtest-results` artifact. It contains `results/` (the leaderboard, details, and JSON) and `data/` (the cached bars, so later runs skip the download).

## Adding a strategy

1. Create `strategies/your_name.py`. Subclass `Strategy` and fill in the description fields
   (name, summary, entry and exit rules, weaknesses, changelog).
2. Write `signals(df)`. It returns 1 (long), -1 (short), or 0 (flat) for each bar, and may only
   use data up to that bar.
3. Import it in `strategies/__init__.py` and add it to `ALL_STRATEGIES`.

## Web dashboard (GitHub Pages)

`index.html` reads `results/dashboard-data.json`, which each run overwrites. After a run, the workflow commits the new results to the repo.

To turn it on:
1. Settings, then Pages. Under "Build and deployment," choose "Deploy from a branch," branch `main`, folder `/ (root)`, and save.
2. Wait a minute, then open the Pages address shown there.

Each run rewrites `results/dashboard-data.json`, and the page shows the newest run after a refresh. Dated files accumulate in `results/` and in the git history, so delete old `backtest-<date>.json` files now and then to keep the repo small.

## Results

Each run writes these files to `results/`:

- `dashboard-data.json`: the file the web page reads. Overwritten each run.

- `leaderboard-<date>.csv`: one row per strategy. Sort by any column.
- `details-<date>.csv`: one row per strategy, stock and period.
- `backtest-<date>.json`: everything, including equity curves and every trade.

Out-of-sample columns come from the last 30% of history, which the screen never saw.
A large `overfit_gap_pct` (in-sample return minus out-of-sample return) is a warning sign.

## Known limits (version 1)

- Daily bars only in the example config. Intraday works, but the runner is not tuned for speed on years of 1-minute data.
- Stop-loss and take-profit (engine version 2) are checked on each bar's high and low, so an intraday touch counts. Daily bars can't show the order in which the high and low happened. If a bar hits both levels, the stop is assumed to fill first.
- Fees use the rates in `config.json`. Check them against current SEC and FINRA published rates.
- Results on the sample data in testing are fake, because they come from random numbers. Only real market data gives meaningful results.
