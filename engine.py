"""
engine.py: Part 2's backtest engine (Person 2), ported from the group notebook.

`make_weights` and `backtest` are copied from notebook cells 2.2–2.6.
The only change: lookback and rebalancing frequency are now arguments, so
app users can vary them. With the defaults (60 days, "Monthly") the code
path is identical to the notebook.

Timing (no look-ahead): the volatility at a month-end close uses the 60 returns
up to and including that close. The weights decided then are held during the
NEXT month (weights.shift(1)), so they never earn the return that ends on
their own signal date.
"""
import numpy as np
import pandas as pd

FREQ_RULE = {"Monthly": "ME", "Quarterly": "QE", "Annual": "YE"}
PERIODS_PER_YEAR = {"Monthly": 12, "Quarterly": 4, "Annual": 1}


def make_weights(prices: pd.DataFrame, vol_window: int = 60, freq: str = "Monthly") -> pd.DataFrame:
    """Inverse-volatility target weights, decided at each period-end close."""
    v = prices.pct_change().rolling(window=vol_window).std() * np.sqrt(252)
    w = (1 / v).div((1 / v).sum(axis=1), axis=0)
    return w.resample(FREQ_RULE[freq]).last().dropna()


def period_returns(prices: pd.DataFrame, freq: str = "Monthly") -> pd.DataFrame:
    """Simple returns between period-end closes."""
    return prices.resample(FREQ_RULE[freq]).last().pct_change()


def backtest(weights, monthly_rets, tc_bps=10):
    """weights: target weights decided at each month-end. Returns monthly gross/net returns, turnover and costs."""
    rets = monthly_rets.loc[weights.index, weights.columns]
    w_held = weights.shift(1)                                    # weights held during month t (decided at t-1)

    gross = (w_held * rets).sum(axis=1, min_count=1)            # min_count=1 -> NaN (not 0) when nothing is held yet

    w_drift = (w_held * (1 + rets)).div(1 + gross, axis=0)     # weights just before rebalancing at end of t
    turnover = (weights - w_drift.fillna(0)).abs().sum(axis=1) # first month: from cash -> turnover = 1

    cost = turnover.shift(1) * tc_bps / 10_000                 # traded at end of t-1 -> paid in month t
    net = gross - cost

    out = pd.DataFrame({'gross_ret': gross, 'net_ret': net, 'turnover': turnover.shift(1), 'cost': cost})
    return out.dropna()


def run(prices: pd.DataFrame, benchmark_target: pd.Series, lookback: int = 60,
        tc_bps: float = 10, freq: str = "Monthly", bench_tc_bps: float | None = None):
    """Strategy and 60/40 run through the same engine (notebook cell 2.5).

    Returns (weights, bt_strategy, bt_benchmark). The benchmark uses the same
    dates as the strategy, so both series start together.
    """
    weights = make_weights(prices, lookback, freq)
    rets = period_returns(prices, freq)
    bt_strategy = backtest(weights, rets, tc_bps=tc_bps)

    target = benchmark_target.reindex(weights.columns, fill_value=0.0)
    weights_bm = pd.DataFrame([target] * len(weights), index=weights.index)
    bt_bm = backtest(weights_bm, rets, tc_bps=tc_bps if bench_tc_bps is None else bench_tc_bps)
    return weights, bt_strategy, bt_bm
