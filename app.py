"""
app.py: Streamlit front end for the Inverse-Volatility (Risk Parity) strategy.

Run locally:   streamlit run app.py
Calculations live in data.py (Part 1), engine.py (Part 2) and metrics.py
(Part 3), copied from the group notebook so the results match it.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

import config as C
from data import load_all
from engine import FREQ_RULE, PERIODS_PER_YEAR, run
from metrics import perf_table, wealth

st.set_page_config(page_title="Inverse-Volatility Multi-Asset Strategy", layout="wide")


# ---------------------------------------------------------------- data (cached for 1 day)
@st.cache_data(ttl=24 * 3600, show_spinner="Downloading prices (Yahoo Finance) and T-bill yields (FRED)…")
def get_data():
    return load_all()


# ---------------------------------------------------------------- sidebar
st.sidebar.header("Change the assumptions")
lookback = st.sidebar.slider("Volatility lookback (trading days)", 20, 252, C.LOOKBACK, 5)
tc_bps = st.sidebar.slider("Transaction cost (bps per unit of turnover)", 0, 50, C.REBALANCE_COST_BPS, 1)
freq = st.sidebar.selectbox("Rebalancing frequency", list(FREQ_RULE), index=0)
with st.sidebar.expander("Advanced"):
    log_scale = st.checkbox("Log scale for cumulative chart", False)

baseline = (lookback == C.LOOKBACK and tc_bps == C.REBALANCE_COST_BPS
            and freq == C.REBAL_FREQ)
if baseline:
    st.sidebar.success("Baseline settings: results match the prospectus.")
else:
    st.sidebar.warning("Custom settings: results differ from the prospectus.")
if st.sidebar.button("Reset to baseline"):
    st.session_state.clear()
    st.rerun()

# ---------------------------------------------------------------- run
st.title("Inverse-Volatility Multi-Asset Portfolio")
st.caption("SPY · IEF · GLD · SHY weighted by 1/σ, versus a 60/40 SPY/IEF benchmark. "
           "Educational project. Not investment advice.")

try:
    adjusted_close, risk_free_daily = get_data()
except Exception as e:  # show the problem instead of a blank page
    st.error(f"Data download failed: {e}")
    st.stop()

prices = adjusted_close.loc[:, list(C.TICKERS)]
weights, bt_s, bt_b = run(prices, C.BENCHMARK_TARGET, lookback, tc_bps, freq)
ppy, rule = PERIODS_PER_YEAR[freq], FREQ_RULE[freq]
table = perf_table(bt_s, bt_b, risk_free_daily, rule, ppy)
m_s = table.loc["Inverse Vol (net)"]          # strategy, net of costs
m_b = table.loc["60/40 Benchmark (gross)"]    # primary benchmark (Part 1 / Part 3)
rp = bt_s["net_ret"]

st.write(f"**Backtest:** {rp.index[0]:%b %Y} → {rp.index[-1]:%b %Y} · {len(rp)} {freq.lower()} returns · "
         f"net of {tc_bps} bps costs · data to {C.SAMPLE_END:%d %b %Y}")

st.caption("Headline figures: Inverse-Vol **net** of costs; differences are versus the 60/40 **gross** benchmark.")
k = st.columns(4)
k[0].metric("Sharpe ratio", f"{m_s['Sharpe ratio']:.2f}",
            f"{m_s['Sharpe ratio'] - m_b['Sharpe ratio']:+.2f} vs 60/40")
k[1].metric("Ann. volatility", f"{m_s['Annualised volatility']:.2%}",
            f"{m_s['Annualised volatility'] - m_b['Annualised volatility']:+.2%} vs 60/40", delta_color="inverse")
k[2].metric("Max drawdown", f"{m_s['Max Drawdown']:.2%}",
            f"{m_s['Max Drawdown'] - m_b['Max Drawdown']:+.2%} vs 60/40")
k[3].metric("Ann. average return", f"{m_s['Annualised avg return']:.2%}",
            f"{m_s['Annualised avg return'] - m_b['Annualised avg return']:+.2%} vs 60/40")

tab_perf, tab_alloc, tab_method = st.tabs(["Performance", "Allocation & costs", "Methodology"])

# ---------------------------------------------------------------- performance
with tab_perf:
    cum = pd.DataFrame({
        "Inverse Vol (gross)": wealth(bt_s["gross_ret"], rule),
        "Inverse Vol (net)": wealth(bt_s["net_ret"], rule),
        "60/40 (gross)": wealth(bt_b["gross_ret"], rule),
        "60/40 (net)": wealth(bt_b["net_ret"], rule),
    })
    fig = px.line(cum, labels={"value": "Value (start = 1)", "index": "", "variable": ""},
                  title="Cumulative performance, all series starting at 1", log_y=log_scale,
                  color_discrete_sequence=["#A47232", "#A47232", "#25486C", "#25486C"])
    for tr in fig.data:
        if "(net)" in tr.name:
            tr.line.dash = "dash"
        tr.name = f"{tr.name} · {cum[tr.name].iloc[-1]:.2f}x"

    fig.update_layout(legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig, width="stretch")

    dd = cum[["Inverse Vol (net)", "60/40 (net)"]]
    dd = dd / dd.cummax() - 1
    fig_dd = px.area(dd, labels={"value": "Drawdown", "index": "", "variable": ""},
                     title="Drawdown from previous peak")
    fig_dd.update_layout(yaxis_tickformat=".0%", legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig_dd, width="stretch")

    st.subheader("Performance measures")
    st.dataframe(table.style.format({
        "Annualised avg return": "{:.2%}", "Annualised volatility": "{:.2%}",
        "Sharpe ratio": "{:.2f}", "Max Drawdown": "{:.2%}", "Beta (non-ann.)": "{:.2f}",
        "Alpha (ann.)": "{:.2%}", "Information Ratio": "{:.2f}"}, na_rep="—"), width="stretch")
    st.caption(f"Computed from {freq.lower()} simple returns: mean ×{ppy}, standard deviation ×√{ppy} "
               "(sample, ddof=1). Risk-free: FRED 3-month Treasury yield compounded within each period. "
               "Beta, Alpha and IR are measured against the 60/40 **gross** benchmark. Beta is the slope "
               "of excess returns and is NOT annualised; Alpha is Jensen's alpha, annualised.")

    st.download_button("Download returns (CSV)",
                       pd.concat({"strategy": bt_s, "benchmark_6040": bt_b}, axis=1).to_csv(),
                       "backtest_returns.csv", "text/csv")

# ---------------------------------------------------------------- allocation
with tab_alloc:
    w_used = weights.loc[weights.index < rp.index[-1]]   # weights actually held at some point
    fig_w = px.area(w_used, labels={"value": "Weight", "index": "", "variable": ""},
                    title="Inverse-volatility target weights at each rebalance")
    fig_w.update_layout(yaxis_tickformat=".0%", legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig_w, width="stretch")

    c = st.columns(3)
    c[0].metric("Average SHY weight", f"{w_used['SHY'].mean():.0%}")
    c[1].metric(f"Avg turnover per rebalance (after the first)", f"{bt_s['turnover'].iloc[1:].mean():.2%}")
    c[2].metric("Cost drag per year", f"{bt_s['cost'].mean() * ppy:.3%}")

    st.subheader("Average and latest weights")
    st.dataframe(pd.DataFrame({"Average": w_used.mean(), f"Latest ({w_used.index[-1]:%b %Y})": w_used.iloc[-1]})
                 .style.format("{:.1%}"))

# ---------------------------------------------------------------- methodology
with tab_method:
    st.markdown(f"""
**Allocation rule.** At each {freq.lower()}-end close, compute each ETF's standard deviation of
daily returns over the last **{lookback}** trading days (data known at that close only), and set

$$w_i = \\frac{{1/\\sigma_i}}{{\\sum_{{j=1}}^{{4}} 1/\\sigma_j}}$$

These weights are held during the **next** period, so a signal never earns the return that ends
on its own signal date. Within the period the holdings drift with prices.

**Costs.** {tc_bps} bps × turnover, where turnover = Σ|w_target − w_drifted| (the first trade, from
cash, counts as turnover of 100%). The cost is deducted from the following period's return.

**Data.** Daily adjusted closes (splits and distributions included) from the Yahoo Finance chart
API, checked against the NYSE trading calendar. Risk-free rate: FRED DGS3MO, using for each day the
latest yield dated strictly earlier, divided by 100 and 252. Sample: {C.SAMPLE_START:%d %b %Y} –
{C.SAMPLE_END:%d %b %Y}; base close {C.BASE_DATE:%d %b %Y}.

**Benchmark.** 60% SPY / 40% IEF, rebalanced on the same schedule by the same engine.

**Limitations.** This is a historical backtest. The sample covers a long bond bull market, and
SHY's low volatility gives it most of the weight (concentration). Execution at the close is assumed.
""")
