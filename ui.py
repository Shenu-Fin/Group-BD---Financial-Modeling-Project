"""
ui.py: presentation helpers for the Streamlit app (palette, CSS, page header,
section titles, chart styling). No calculations live here.
"""
from html import escape

import streamlit as st

# ---------------------------------------------------------------- palette
NAVY = "#0F2340"
STRATEGY = "#1B365D"      # Inverse-Vol series
BENCHMARK = "#8FA6C7"     # 60/40 series
ACCENT = "#4A6FA5"
LIGHT = "#C2CCD8"
GRID = "#EDF0F4"
INK = "#14233B"
MUTED = "#5B6B82"
BORDER = "#DDE3EA"
ASSET_COLORS = {"SPY": STRATEGY, "IEF": ACCENT, "GLD": BENCHMARK, "SHY": "#D3DCE8"}

_CSS = f"""
<style>
html, body, [class*="st-"] {{ font-variant-numeric: tabular-nums; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1480px; }}

/* sidebar */
[data-testid="stSidebar"] {{ border-right: 1px solid #243E66; }}
[data-testid="stSidebarNavSeparator"] {{ border-color: #243E66; }}
[data-testid="stSidebarNav"] [data-testid="stNavSectionHeader"] {{
    color: #7F93B3; font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 600; }}
[data-testid="stSidebarNav"] a span {{ font-size: 0.86rem; }}
.sb-block {{ border-top: 1px solid #243E66; padding-top: 0.9rem; margin-top: 0.4rem; }}
.sb-label {{ color: #7F93B3; font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 600; margin-bottom: 0.45rem; }}
.sb-row {{ display: flex; justify-content: space-between; font-size: 0.8rem; padding: 0.18rem 0; color: #D5DDEA; }}
.sb-row span:first-child {{ color: #8FA6C7; }}
.sb-foot {{ color: #6F84A6; font-size: 0.72rem; line-height: 1.45; margin-top: 1.2rem; }}

/* page header */
.hdr {{ border-bottom: 1px solid {BORDER}; padding-bottom: 1.1rem; margin-bottom: 1.4rem; }}
.hdr-top {{ display: flex; justify-content: space-between; align-items: center; gap: 1rem; }}
.eyebrow {{ color: {MUTED}; font-size: 0.74rem; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 600; }}
.hdr h1 {{ font-size: 1.75rem; font-weight: 600; color: {INK}; margin: 0.35rem 0 0.25rem 0; padding: 0; letter-spacing: -0.01em; }}
.hdr .lede {{ color: {MUTED}; font-size: 0.88rem; margin: 0 0 0.9rem 0; }}
.meta {{ display: flex; flex-wrap: wrap; gap: 0; border: 1px solid {BORDER}; border-radius: 4px; background: #FAFBFC; }}
.meta div {{ padding: 0.5rem 1.1rem; border-right: 1px solid {BORDER}; }}
.meta div:last-child {{ border-right: none; }}
.meta span {{ display: block; color: {MUTED}; font-size: 0.66rem; letter-spacing: 0.08em; text-transform: uppercase; font-weight: 600; }}
.meta b {{ color: {INK}; font-size: 0.86rem; font-weight: 600; }}
.status {{ font-size: 0.74rem; font-weight: 600; padding: 0.22rem 0.6rem; border-radius: 3px; border: 1px solid; white-space: nowrap; }}
.status.ok {{ color: #1E5B3C; background: #EEF6F1; border-color: #CFE3D7; }}
.status.custom {{ color: #7A4B0E; background: #FBF5EA; border-color: #EBDCC0; }}

/* section titles */
.sec {{ display: flex; justify-content: space-between; align-items: baseline; margin: 1.6rem 0 0.6rem 0; }}
.sec h3 {{ font-size: 0.8rem; letter-spacing: 0.09em; text-transform: uppercase; color: {INK}; font-weight: 700; margin: 0; padding: 0; }}
.sec span {{ color: {MUTED}; font-size: 0.78rem; }}
.panel-title {{ font-size: 0.92rem !important; font-weight: 600; color: {INK}; margin: 0; }}
.panel-sub {{ font-size: 0.76rem !important; color: {MUTED}; margin: 0.1rem 0 0.3rem 0; }}
.note {{ color: {MUTED}; font-size: 0.76rem !important; line-height: 1.5; margin-top: 0.35rem; }}
[data-testid="stTable"] table {{ font-size: 0.82rem; }}
[data-testid="stTable"] th {{ color: {MUTED}; font-weight: 600; }}
.fixed {{ font-size: 0.82rem !important; }}
.fixed div {{ display: flex; justify-content: space-between; border-bottom: 1px solid #EEF1F5; padding: 0.42rem 0; }}
.fixed div span:first-child {{ color: {MUTED}; }}
.fixed div span:last-child {{ color: {INK}; font-weight: 500; text-align: right; }}

/* KPI cards (st.metric) */
[data-testid="stMetric"] {{
    background: #FFFFFF; border: 1px solid {BORDER}; border-top: 3px solid {STRATEGY};
    border-radius: 4px; padding: 0.85rem 1rem 0.75rem 1rem; box-shadow: 0 1px 2px rgba(15,35,64,0.04); }}
[data-testid="stMetricLabel"] p {{ font-size: 0.7rem !important; letter-spacing: 0.08em; text-transform: uppercase; color: {MUTED}; font-weight: 600; }}
[data-testid="stMetricValue"] {{ font-size: 1.65rem !important; font-weight: 600; color: {INK}; }}
[data-testid="stMetricDelta"] {{ font-size: 0.76rem; }}
/* narrow windows: shrink the numbers instead of cutting them off ("3....") */
[data-testid="stMetricValue"] {{ font-size: clamp(1.05rem, 1.7vw, 1.65rem) !important; }}
[data-testid="stMetricValue"] > div, [data-testid="stMetricDelta"] > div {{
    overflow: visible !important; text-overflow: clip !important; }}
[data-testid="stMetricLabel"] p, [data-testid="stMetricLabel"] div {{
    white-space: normal !important; overflow: visible !important; text-overflow: clip !important; }}
[data-testid="stMetricDelta"] > div {{ white-space: normal !important; }}
[data-testid="stMetricLabel"] p {{ word-break: normal !important; overflow-wrap: normal !important; }}
/* KPI rows wrap onto a second line instead of squeezing the cards */
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] [data-testid="stMetric"]) {{ flex-wrap: wrap; row-gap: 0.75rem; }}
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] [data-testid="stMetric"]) > [data-testid="stColumn"] {{ min-width: 150px !important; flex: 1 1 150px !important; }}
@media (max-width: 1200px) {{
    [data-testid="stMetric"] {{ padding: 0.7rem 0.6rem 0.6rem 0.6rem; }}
}}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def header(title: str, lede: str, meta: dict, baseline: bool) -> None:
    status = ('<span class="status ok">● Baseline · matches prospectus</span>' if baseline
              else '<span class="status custom">● Custom assumptions · differs from prospectus</span>')
    cells = "".join(f"<div><span>{escape(k)}</span><b>{escape(v)}</b></div>" for k, v in meta.items())
    st.markdown(f"""
<div class="hdr">
  <div class="hdr-top">
    <div class="eyebrow">DIVMA · Dynamic Inverse-Volatility Multi-Asset Strategy</div>{status}
  </div>
  <h1>{escape(title)}</h1>
  <p class="lede">{escape(lede)}</p>
  <div class="meta">{cells}</div>
</div>""", unsafe_allow_html=True)


def section(title: str, note: str = "") -> None:
    st.markdown(f'<div class="sec"><h3>{escape(title)}</h3><span>{escape(note)}</span></div>',
                unsafe_allow_html=True)


def panel_title(title: str, sub: str = "") -> None:
    st.markdown(f'<div class="panel-title">{escape(title)}</div><div class="panel-sub">{escape(sub)}</div>',
                unsafe_allow_html=True)


def note(text: str) -> None:
    st.markdown(f'<div class="note">{text}</div>', unsafe_allow_html=True)


def fixed_list(rows: dict) -> None:
    body = "".join(f"<div><span>{escape(k)}</span><span>{escape(v)}</span></div>" for k, v in rows.items())
    st.markdown(f'<div class="fixed">{body}</div>', unsafe_allow_html=True)


def style_fig(fig, height: int = 340, pct_axis: bool = False):
    """Restrained institutional chart styling."""
    fig.update_layout(
        height=height, template="none", paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=11.5, color="#33425B"),
        margin=dict(l=8, r=8, t=8, b=8), hovermode="x unified", title=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                    font=dict(size=11), title=None, bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="white", bordercolor=BORDER, font_size=11),
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER, ticks="outside", tickcolor=BORDER, title=None)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor="rgba(0,0,0,0)", title=None)
    if pct_axis:
        fig.update_yaxes(tickformat=".0%")
    return fig
