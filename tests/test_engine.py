"""Offline tests on synthetic prices. Run with:  pytest -q"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import pytest

from engine import make_weights, period_returns, run
from metrics import perf_table

TICKERS = ["SPY", "IEF", "GLD", "SHY"]
BM = pd.Series({"SPY": 0.6, "IEF": 0.4})


@pytest.fixture
def prices():
    rng = np.random.default_rng(0)
    idx = pd.bdate_range("2015-01-01", "2019-12-31")
    rets = rng.normal(0.0003, [0.012, 0.005, 0.010, 0.001], size=(len(idx), 4))
    return pd.DataFrame(100 * np.cumprod(1 + rets, axis=0), index=idx, columns=TICKERS)


@pytest.mark.parametrize("freq", ["Monthly", "Quarterly"])
def test_no_lookahead(prices, freq):
    """Scrambling prices AFTER a cutoff must not change results ON or BEFORE it."""
    w, s, _ = run(prices, BM, 60, 10, freq)
    cut = w.index[len(w) // 2]
    shocked = prices.copy()
    after = shocked.index > cut
    shocked.loc[after] *= np.random.default_rng(1).uniform(0.5, 1.5, size=shocked.loc[after].shape)
    w2, s2, _ = run(shocked, BM, 60, 10, freq)
    pd.testing.assert_frame_equal(w.loc[:cut], w2.loc[:cut])
    pd.testing.assert_frame_equal(s.loc[:cut], s2.loc[:cut])


def test_weights_long_only_sum_to_one(prices):
    w = make_weights(prices, 60)
    assert (w > 0).all().all() and np.allclose(w.sum(axis=1), 1)


def test_hand_check_one_month(prices):
    w, s, _ = run(prices, BM, 60, 0)
    r = period_returns(prices)
    m = s.index[12]
    prev = w.index[w.index.get_loc(m) - 1]
    assert abs((w.loc[prev] * r.loc[m]).sum() - s.loc[m, "gross_ret"]) < 1e-12
    assert np.allclose(s["net_ret"], s["gross_ret"])           # zero cost -> net = gross


def test_benchmark_aligned_and_metrics_finite(prices):
    _, s, b = run(prices, BM)
    assert s.index.equals(b.index)
    t = perf_table(s, b, pd.Series(0.0001, index=prices.index))
    assert np.isfinite(t.drop(columns="Information Ratio").to_numpy()).all()
    assert t.loc["60/40 Benchmark (gross)", "Beta (non-ann.)"] == 1.0
