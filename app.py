"""
app.py: Streamlit front end for the Inverse-Volatility (Risk Parity) strategy.

Run locally:   streamlit run app.py
Calculations live in data.py (Part 1), engine.py (Part 2) and metrics.py
(Part 3), copied from the group notebook so the results match it.
Presentation helpers (theme, header, chart styling) live in ui.py.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import config as C
import ui
from data import load_all
from engine import FREQ_RULE, PERIODS_PER_YEAR, run
from metrics import perf_table, wealth

st.set_page_config(page_title="DIVMA · Inverse-Volatility Multi-Asset Strategy", layout="wide",
                   initial_sidebar_state="expanded")
ui.inject_css()
st.logo("assets/logo.svg", size="large")

S_NET, B_GROSS = "Inverse Vol (net)", "60/40 Benchmark (gross)"


# ---------------------------------------------------------------- data (cached for 1 day)
@st.cache_data(ttl=24 * 3600, show_spinner="Downloading prices (Yahoo Finance) and T-bill yields (FRED)…")
def get_data():
    return load_all()


# ---------------------------------------------------------------- assumptions (shared by all pages)
DEFAULTS = {"lookback": C.LOOKBACK, "tc_bps": C.REBALANCE_COST_BPS, "freq": C.REBAL_FREQ,
            "bench_costs": True, "log_scale": False}
for _k, _v in DEFAULTS.items():
    st.session_state.setdefault(_k, _v)


def _save(k):
    st.session_state[k] = st.session_state[f"w_{k}"]


def _widget(fn, k, label, **kw):
    """Widgets keep their value when the user switches page (Streamlit drops widget state otherwise)."""
    st.session_state[f"w_{k}"] = st.session_state[k]
    return fn(label, key=f"w_{k}", on_change=_save, args=(k,), **kw)


def _reset():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v


A = st.session_state
lookback, tc_bps, freq = int(A.lookback), int(A.tc_bps), A.freq
bench_tc = None if A.bench_costs else 0
baseline = (lookback == C.LOOKBACK and tc_bps == C.REBALANCE_COST_BPS
            and freq == C.REBAL_FREQ and A.bench_costs)

# ---------------------------------------------------------------- run the model
def run_model(prices, lookback, tc_bps, freq, bench_tc):
    """engine.run, with returns clipped to the sample start. Short lookbacks would otherwise
    start before the risk-free series and break perf_table; the baseline is unaffected."""
    w, s, b = run(prices, C.BENCHMARK_TARGET, lookback, tc_bps, freq, bench_tc)
    return w, s.loc[C.SAMPLE_START:], b.loc[C.SAMPLE_START:]


try:
    adjusted_close, risk_free_daily = get_data()
except Exception as e:  # show the problem instead of a blank page
    st.error(f"Data download failed: {e}")
    st.stop()

prices = adjusted_close.loc[:, list(C.TICKERS)]
weights, bt_s, bt_b = run_model(prices, lookback, tc_bps, freq, bench_tc)
ppy, rule = PERIODS_PER_YEAR[freq], FREQ_RULE[freq]
table = perf_table(bt_s, bt_b, risk_free_daily, rule, ppy)
m_s, m_b = table.loc[S_NET], table.loc[B_GROSS]
rp = bt_s["net_ret"]

cum = pd.DataFrame({
    "Inverse Vol (gross)": wealth(bt_s["gross_ret"], rule),
    "Inverse Vol (net)": wealth(bt_s["net_ret"], rule),
    "60/40 (gross)": wealth(bt_b["gross_ret"], rule),
    "60/40 (net)": wealth(bt_b["net_ret"], rule),
})
period_label = f"{rp.index[0]:%b %Y} – {rp.index[-1]:%b %Y}"
META = {
    "Reporting period": period_label,
    "Observations": f"{len(rp)} {freq.lower()}",
    "Rebalancing": freq,
    "Benchmark": "60/40 SPY / IEF",
    "Transaction cost": f"{tc_bps} bps",
    "Data as of": f"{C.SAMPLE_END:%d %b %Y}",
}


def calendar_returns() -> pd.DataFrame:
    def by_year(r):
        return (1 + r).groupby(r.index.year).prod() - 1
    out = pd.DataFrame({"Inverse Vol (net)": by_year(bt_s["net_ret"]),
                        "60/40 (gross)": by_year(bt_b["gross_ret"])})
    out["Excess"] = out.iloc[:, 0] - out.iloc[:, 1]
    first, last = rp.index[0], rp.index[-1]
    labels = {first.year: f"{first.year} (from {first:%b})", last.year: f"{last.year} (to {last:%b})"}
    out.index = [labels.get(y, str(y)) for y in out.index]
    return out


PERF_FMT = {"Annualised avg return": "{:.2%}", "Annualised volatility": "{:.2%}", "Sharpe ratio": "{:.2f}",
            "Max Drawdown": "{:.2%}", "Beta (non-ann.)": "{:.2f}", "Alpha (ann.)": "{:.2%}",
            "Information Ratio": "{:.2f}"}
PERF_NOTE = (f"Computed from {freq.lower()} simple returns: mean ×{ppy}, standard deviation ×√{ppy} "
             "(sample, ddof=1). Risk-free: FRED 3-month Treasury yield compounded within each period. "
             "Beta, Alpha and IR are measured against the 60/40 <b>gross</b> benchmark. Beta is the slope "
             "of excess returns and is NOT annualised; Alpha is Jensen's alpha, annualised.")


# ---------------------------------------------------------------- shared building blocks
def kpi_row():
    k = st.columns(5)
    k[0].metric("Ann. return", f"{m_s['Annualised avg return']:.2%}",
                f"{m_s['Annualised avg return'] - m_b['Annualised avg return']:+.2%} vs 60/40")
    k[1].metric("Ann. volatility", f"{m_s['Annualised volatility']:.2%}",
                f"{m_s['Annualised volatility'] - m_b['Annualised volatility']:+.2%} vs 60/40",
                delta_color="inverse")
    k[2].metric("Sharpe ratio", f"{m_s['Sharpe ratio']:.2f}",
                f"{m_s['Sharpe ratio'] - m_b['Sharpe ratio']:+.2f} vs 60/40")
    k[3].metric("Max drawdown", f"{m_s['Max Drawdown']:.2%}",
                f"{m_s['Max Drawdown'] - m_b['Max Drawdown']:+.2%} vs 60/40")
    g_s, g_b = cum["Inverse Vol (net)"].iloc[-1], cum["60/40 (gross)"].iloc[-1]
    k[4].metric("Growth of $1", f"{g_s:.2f}x", f"{g_s - g_b:+.2f}x vs 60/40")
    ui.note("Strategy figures are Inverse-Vol <b>net</b> of costs; differences are versus the 60/40 "
            "<b>gross</b> benchmark.")


def cumulative_chart(series, height=340):
    fig = go.Figure()
    styles = {"Inverse Vol (gross)": (ui.STRATEGY, "solid"), "Inverse Vol (net)": (ui.STRATEGY, "dot"),
              "60/40 (gross)": (ui.BENCHMARK, "solid"), "60/40 (net)": (ui.BENCHMARK, "dot")}
    for name in series:
        color, dash = styles[name]
        dash = dash if len(series) > 2 else "solid"
        fig.add_scatter(x=cum.index, y=cum[name], name=f"{name} · {cum[name].iloc[-1]:.2f}x",
                        line=dict(color=color, dash=dash, width=1.8), hovertemplate="%{y:.2f}x")
    if A.log_scale:
        fig.update_yaxes(type="log")
    return ui.style_fig(fig, height)


def drawdown_chart(height=300):
    dd = cum[["Inverse Vol (net)", "60/40 (net)"]]
    dd = dd / dd.cummax() - 1
    fig = go.Figure()
    for name, color in [("60/40 (net)", ui.BENCHMARK), ("Inverse Vol (net)", ui.STRATEGY)]:
        fig.add_scatter(x=dd.index, y=dd[name], name=name, fill="tozeroy", mode="lines",
                        line=dict(color=color, width=1.4), hovertemplate="%{y:.1%}")
    return ui.style_fig(fig, height, pct_axis=True)


def annual_chart(height=340):
    cr = calendar_returns()
    fig = go.Figure()
    fig.add_bar(x=cr.index, y=cr["Inverse Vol (net)"], name="Inverse Vol (net)", marker_color=ui.STRATEGY,
                hovertemplate="%{y:.2%}")
    fig.add_bar(x=cr.index, y=cr["60/40 (gross)"], name="60/40 (gross)", marker_color=ui.BENCHMARK,
                hovertemplate="%{y:.2%}")
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.05)
    fig.update_xaxes(tickangle=-45, tickvals=list(cr.index), ticktext=[s.split(" ")[0] for s in cr.index])
    return ui.style_fig(fig, height, pct_axis=True)


def perf_measures():
    st.table(table.style.format(PERF_FMT, na_rep="—"))
    ui.note(PERF_NOTE)


def assumptions_panel():
    with st.container(border=True):
        left, right = st.columns([3, 2], gap="large")
        with left:
            ui.panel_title("Editable inputs", "Changes re-run the backtest on every page.")
            c = st.columns(2)
            with c[0]:
                _widget(st.number_input, "lookback", "Volatility lookback (trading days)",
                        min_value=20, max_value=252, step=5)
                _widget(st.selectbox, "freq", "Rebalancing frequency", options=list(FREQ_RULE))
            with c[1]:
                _widget(st.number_input, "tc_bps", "Transaction cost (bps of turnover)",
                        min_value=0, max_value=50, step=1)
                st.write("")
                _widget(st.toggle, "bench_costs", "Apply costs to 60/40 too")
                _widget(st.toggle, "log_scale", "Log scale for cumulative charts")
            b = st.columns([1, 2])
            b[0].button("Reset to baseline", on_click=_reset, disabled=baseline, width="stretch")
            with b[1]:
                ui.note("Baseline: 60-day lookback · 10 bps · monthly · costs on both portfolios. "
                        "At baseline the results match the group notebook and the prospectus.")
        with right:
            ui.panel_title("Fixed parameters", "Set in config.py, shared with the notebook.")
            ui.fixed_list({
                "Universe": " · ".join(C.TICKERS),
                "Weighting rule": "w ∝ 1 / σ (daily returns)",
                "Benchmark": "60% SPY / 40% IEF",
                "Sample": f"{C.SAMPLE_START:%d %b %Y} – {C.SAMPLE_END:%d %b %Y}",
                "Base date (value = 1)": f"{C.BASE_DATE:%d %b %Y}",
                "Risk-free rate": f"FRED {C.FRED_SERIES} (3-month T-bill)",
                "Execution": "At the close, held next period",
            })


# ---------------------------------------------------------------- pages
def page_overview():
    ui.header("Portfolio Overview",
              "SPY · IEF · GLD · SHY weighted by 1/σ, versus a 60/40 SPY/IEF benchmark. "
              "Educational project. Not investment advice.", META, baseline)
    ui.section("Model assumptions", "Change the inputs to re-run the backtest")
    assumptions_panel()

    ui.section("Key metrics", f"Backtest {period_label}")
    kpi_row()

    ui.section("Analytics")
    c = st.columns(2, gap="medium")
    with c[0], st.container(border=True):
        ui.panel_title("Cumulative performance", "Value of 1 invested at the base date")
        st.plotly_chart(cumulative_chart(["Inverse Vol (net)", "60/40 (gross)"]), width="stretch")
    with c[1], st.container(border=True):
        ui.panel_title("Calendar-year returns", "Inverse Vol (net) versus 60/40 (gross)")
        st.plotly_chart(annual_chart(), width="stretch")

    ui.section("Performance measures", "All four series")
    perf_measures()


def page_performance():
    ui.header("Performance", "Cumulative growth and period-by-period returns, gross and net of costs.",
              META, baseline)
    kpi_row()
    ui.section("Cumulative performance", "All series start at 1 · dotted = net of costs")
    with st.container(border=True):
        st.plotly_chart(cumulative_chart(list(cum.columns), 420), width="stretch")
    c = st.columns([3, 2], gap="medium")
    with c[0]:
        ui.section("Performance measures")
        perf_measures()
        st.download_button("Download returns (CSV)",
                           pd.concat({"strategy": bt_s, "benchmark_6040": bt_b}, axis=1).to_csv(),
                           "backtest_returns.csv", "text/csv")
    with c[1]:
        ui.section("Calendar-year returns")
        st.dataframe(calendar_returns().style.format("{:.2%}"), width="stretch", height=420)


def page_allocation():
    ui.header("Allocation", "Inverse-volatility target weights decided at each rebalance.", META, baseline)
    w_used = weights.loc[weights.index < rp.index[-1]]   # weights actually held at some point
    k = st.columns(4)
    for i, t in enumerate(C.TICKERS):
        k[i].metric(f"Avg {t} weight", f"{w_used[t].mean():.1%}",
                    f"Latest {w_used[t].iloc[-1]:.1%}", delta_color="off", delta_arrow="off")
    ui.section("Target weights over time", "Stacked, sums to 100%")
    with st.container(border=True):
        fig = go.Figure()
        for t in C.TICKERS:
            fig.add_scatter(x=w_used.index, y=w_used[t], name=t, stackgroup="w", mode="lines",
                            line=dict(width=0.5, color=ui.ASSET_COLORS[t]), hovertemplate="%{y:.1%}")
        st.plotly_chart(ui.style_fig(fig, 400, pct_axis=True), width="stretch")
    ui.section("Average and latest weights")
    st.dataframe(pd.DataFrame({"Average": w_used.mean(), f"Latest ({w_used.index[-1]:%b %Y})": w_used.iloc[-1]})
                 .style.format("{:.1%}"), width="stretch")
    ui.note("SHY's low volatility gives it most of the weight: the portfolio is concentrated in short Treasuries.")


def page_risk():
    ui.header("Risk & Drawdown", "Losses from previous peaks and rolling volatility.", META, baseline)
    r_b = bt_b["net_ret"]
    k = st.columns(4)
    k[0].metric("Max DD · Inverse Vol (net)", f"{table.loc[S_NET, 'Max Drawdown']:.2%}")
    k[1].metric("Max DD · 60/40 (gross)", f"{table.loc[B_GROSS, 'Max Drawdown']:.2%}")
    k[2].metric(f"Worst {freq.lower()} return", f"{rp.min():.2%}", f"{rp.idxmin():%b %Y}",
                delta_color="off", delta_arrow="off")
    k[3].metric(f"Positive {freq.lower()} returns", f"{(rp > 0).mean():.0%}",
                f"60/40: {(r_b > 0).mean():.0%}", delta_color="off", delta_arrow="off")
    ui.section("Drawdown from previous peak", "Net of costs")
    with st.container(border=True):
        st.plotly_chart(drawdown_chart(340), width="stretch")
    win = {"Monthly": 12, "Quarterly": 4, "Annual": 3}[freq]
    ui.section("Rolling volatility", f"Annualised, {win}-period window")
    with st.container(border=True):
        rv = pd.DataFrame({"Inverse Vol (net)": rp, "60/40 (net)": r_b}).rolling(win).std() * ppy ** 0.5
        fig = go.Figure()
        for name, color in [("Inverse Vol (net)", ui.STRATEGY), ("60/40 (net)", ui.BENCHMARK)]:
            fig.add_scatter(x=rv.index, y=rv[name], name=name, line=dict(color=color, width=1.6),
                            hovertemplate="%{y:.1%}")
        st.plotly_chart(ui.style_fig(fig, 320, pct_axis=True), width="stretch")


def rebal_turnover() -> pd.Series:
    """Turnover per rebalance, without the first trade from cash (turnover = 100%).
    That trade is only inside the reporting window when the lookback is 60 days or longer."""
    to = bt_s["turnover"]
    return to.iloc[1:] if to.iloc[0] > 0.999 else to


def page_costs():
    ui.header("Transaction Costs", "Turnover at each rebalance and its drag on returns.", META, baseline)
    gap = m_s["Annualised avg return"] - table.loc["Inverse Vol (gross)", "Annualised avg return"]
    k = st.columns(4)
    k[0].metric("Cost rate", f"{tc_bps} bps", "per unit of turnover", delta_color="off", delta_arrow="off")
    k[1].metric("Avg turnover", f"{rebal_turnover().mean():.2%}", "per rebalance, after the first",
                delta_color="off", delta_arrow="off")
    k[2].metric("Cost drag per year", f"{bt_s['cost'].mean() * ppy:.3%}")
    k[3].metric("Net − gross ann. return", f"{gap:.3%}")
    ui.section("Turnover per rebalance", "First trade from cash (100%) excluded")
    with st.container(border=True):
        to = rebal_turnover()
        fig = go.Figure(go.Bar(x=to.index, y=to, marker_color=ui.ACCENT, hovertemplate="%{y:.2%}",
                               name="Turnover"))
        st.plotly_chart(ui.style_fig(fig, 340, pct_axis=True), width="stretch")
    ui.note("Cost = bps × turnover, where turnover = Σ|w<sub>target</sub> − w<sub>drifted</sub>|. "
            "The cost is deducted from the following period's return.")


@st.cache_data(show_spinner="Running the sensitivity grid…")
def sensitivity_grid(_prices, _rf, freq, bench_costs, lookbacks, costs):
    rows = []
    for lb in lookbacks:
        for c in costs:
            _, s, b = run_model(_prices, lb, c, freq, None if bench_costs else 0)
            t = perf_table(s, b, _rf, FREQ_RULE[freq], PERIODS_PER_YEAR[freq]).loc[S_NET]
            rows.append({"lookback": lb, "cost": c, "Sharpe": t["Sharpe ratio"],
                         "Return": t["Annualised avg return"], "MaxDD": t["Max Drawdown"]})
    return pd.DataFrame(rows)


def page_sensitivity():
    ui.header("Sensitivity Analysis", "Inverse Vol (net) across lookback windows and cost levels.",
              META, baseline)
    lookbacks = (20, 40, 60, 90, 120, 180, 252)
    costs = (0, 5, 10, 20, 30, 50)
    g = sensitivity_grid(prices, risk_free_daily, freq, bool(A.bench_costs), lookbacks, costs)

    def heat(col, fmt, scale):
        z = g.pivot(index="lookback", columns="cost", values=col)
        fig = go.Figure(go.Heatmap(
            z=z.values, x=[f"{c} bps" for c in z.columns], y=[f"{l}d" for l in z.index],
            colorscale=scale, showscale=False, xgap=2, ygap=2,
            text=[[fmt.format(v) for v in row] for row in z.values], texttemplate="%{text}",
            textfont=dict(size=11), hovertemplate="Lookback %{y} · cost %{x}<br>%{text}<extra></extra>"))
        fig = ui.style_fig(fig, 360)
        fig.update_layout(hovermode="closest")
        fig.update_xaxes(side="top", ticks="", linecolor="rgba(0,0,0,0)")
        fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
        return fig

    blues = [[0, "#F1F4F8"], [0.5, "#8FA6C7"], [1, "#1B365D"]]
    c = st.columns(2, gap="medium")
    with c[0], st.container(border=True):
        ui.panel_title("Sharpe ratio", "Rows: volatility lookback · columns: transaction cost")
        st.plotly_chart(heat("Sharpe", "{:.2f}", blues), width="stretch")
    with c[1], st.container(border=True):
        ui.panel_title("Annualised average return", "Rows: volatility lookback · columns: transaction cost")
        st.plotly_chart(heat("Return", "{:.2%}", blues), width="stretch")
    ui.note(f"Each cell re-runs the full backtest at {freq.lower()} rebalancing "
            f"({'costs applied to both portfolios' if A.bench_costs else 'benchmark without costs'}). "
            "Baseline: 60d · 10 bps. Change the frequency in Model assumptions on the Overview page.")


def page_methodology():
    ui.header("Methodology", "How the weights, costs and benchmark are computed.", META, baseline)
    st.markdown(f"""
**Allocation rule.** At each {freq.lower()}-end close, compute each ETF's standard deviation of
daily returns over the last **{lookback}** trading days (data known at that close only), and set

$$w_i = \\frac{{1/\\sigma_i}}{{\\sum_{{j=1}}^{{4}} 1/\\sigma_j}}$$

These weights are held during the **next** period, so a signal never earns the return that ends
on its own signal date. Within the period the holdings drift with prices.

**Costs.** {tc_bps} bps × turnover, where turnover = Σ|w_target − w_drifted| (the first trade, from
cash, counts as turnover of 100%). The cost is deducted from the following period's return.

**Reporting window.** Results are always reported from {C.SAMPLE_START:%d %b %Y}, so every setting
covers the same period as the prospectus. With a lookback shorter than 60 days the first weights
exist before that date, so the first trade from cash (and its cost) falls before the reporting
window and is not shown. At the baseline (60 days) the first trade is included, as in the notebook.

**Data.** Daily adjusted closes (splits and distributions included) from the Yahoo Finance chart
API, checked against the NYSE trading calendar. Risk-free rate: FRED DGS3MO, using for each day the
latest yield dated strictly earlier, divided by 100 and 252. Sample: {C.SAMPLE_START:%d %b %Y} –
{C.SAMPLE_END:%d %b %Y}; base close {C.BASE_DATE:%d %b %Y}.

**Benchmark.** 60% SPY / 40% IEF, rebalanced on the same schedule by the same engine.

**Limitations.** This is a historical backtest. The sample covers a long bond bull market, and
SHY's low volatility gives it most of the weight (concentration). Execution at the close is assumed.
""")


# ---------------------------------------------------------------- navigation
overview = st.Page(page_overview, title="Overview", icon=":material/dashboard:", default=True)
nav = st.navigation({
    "Dashboard": [overview],
    "Analysis": [
        st.Page(page_performance, title="Performance", icon=":material/show_chart:", url_path="performance"),
        st.Page(page_allocation, title="Allocation", icon=":material/donut_large:", url_path="allocation"),
        st.Page(page_risk, title="Risk & Drawdown", icon=":material/trending_down:", url_path="risk"),
        st.Page(page_costs, title="Transaction Costs", icon=":material/receipt_long:", url_path="costs"),
    ],
    "Model": [
        st.Page(page_sensitivity, title="Sensitivity Analysis", icon=":material/grid_on:", url_path="sensitivity"),
        st.Page(page_methodology, title="Methodology", icon=":material/menu_book:", url_path="methodology"),
    ],
})

with st.sidebar:
    rows = {"Lookback": f"{lookback} days", "Cost": f"{tc_bps} bps", "Rebalancing": freq,
            "Benchmark costs": "On" if A.bench_costs else "Off"}
    body = "".join(f'<div class="sb-row"><span>{k}</span><span>{v}</span></div>' for k, v in rows.items())
    state = "Baseline" if baseline else "Custom"
    st.markdown(f'<div class="sb-block"><div class="sb-label">Active assumptions · {state}</div>{body}</div>',
                unsafe_allow_html=True)
    if nav.title != "Overview":
        st.page_link(overview, label="Edit assumptions", icon=":material/tune:")
    st.markdown('<div class="sb-foot">2270 Financial Modeling · Group BD<br>'
                'Educational project. Not investment advice.</div>', unsafe_allow_html=True)

nav.run()
