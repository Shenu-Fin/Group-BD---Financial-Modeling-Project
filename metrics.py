"""
metrics.py: Part 3's performance measures (Person 3, Margarida), ported from
the group notebook (cells 3.1–3.2).

Conventions (notebook 3.1):
  * periodic simple returns from the Part 2 engine (monthly in the baseline)
  * annualisation: mean × 12, std × √12  (generalised to the rebalancing frequency)
  * risk-free: Part 1's daily rf compounded within each period
  * sample standard deviations (ddof=1)
  * Beta, Alpha and IR are measured against the 60/40 GROSS series (Part 1's primary benchmark)
  * Beta is NOT annualised; Alpha (Jensen) is annualised
"""
import numpy as np
import pandas as pd


def period_rf(risk_free_daily: pd.Series, rule: str = "ME") -> pd.Series:
    """Part 1's daily rf compounded within each period ("Passar a risk-free diária para mensal")."""
    return (1 + risk_free_daily).resample(rule).prod() - 1


def wealth(r: pd.Series, rule: str = "ME") -> pd.Series:
    """Cumulative value starting at exactly 1.0 one period before the first return
    (= BASE_DATE, 28 Feb 2005, in the monthly baseline)."""
    w = (1 + r).cumprod()
    start = pd.Series([1.0], index=[w.index[0] - pd.tseries.frequencies.to_offset(rule)])
    return pd.concat([start, w])


def perf_table(bt_strategy: pd.DataFrame, bt_6040: pd.DataFrame, risk_free_daily: pd.Series,
               rule: str = "ME", ppy: int = 12) -> pd.DataFrame:
    """Same loop as notebook cell 3.2, returning the same `perf_table`."""
    rf_m = period_rf(risk_free_daily, rule)
    rf_m = rf_m.loc[bt_strategy.index]

    bench = bt_6040["gross_ret"]
    bench_ex = bench - rf_m

    series = {
        "Inverse Vol (gross)": bt_strategy["gross_ret"],
        "Inverse Vol (net)": bt_strategy["net_ret"],
        "60/40 Benchmark (gross)": bt_6040["gross_ret"],
        "60/40 Benchmark (net)": bt_6040["net_ret"],
    }

    rows = []
    for name, r in series.items():
        ex = r - rf_m
        active = r - bench

        ann_ret = r.mean() * ppy
        ann_vol = r.std() * np.sqrt(ppy)
        sharpe = (ex.mean() / ex.std()) * np.sqrt(ppy)

        nav = pd.concat([pd.Series([1.0]), (1 + r).cumprod()])
        max_dd = (nav / nav.cummax() - 1).min()

        if name == "60/40 Benchmark (gross)":
            beta, alpha, ir = 1.0, 0.0, np.nan
        else:
            beta = ex.cov(bench_ex) / bench_ex.var()
            alpha = (ex.mean() - beta * bench_ex.mean()) * ppy
            ir = (active.mean() / active.std()) * np.sqrt(ppy)

        rows.append({
            "Portfolio": name,
            "Annualised avg return": ann_ret,
            "Annualised volatility": ann_vol,
            "Sharpe ratio": sharpe,
            "Max Drawdown": max_dd,
            "Beta (non-ann.)": beta,
            "Alpha (ann.)": alpha,
            "Information Ratio": ir,
        })

    return pd.DataFrame(rows).set_index("Portfolio")
