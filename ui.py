"""
ui.py: presentation helpers for the Streamlit app (palette, CSS, page header,
section titles, chart styling). No calculations live here.

Look: a money-app account view. Soft grey ground, white rounded tiles,
one violet ink for the strategy, Manrope throughout.
"""
from html import escape

import streamlit as st

# ---------------------------------------------------------------- palette
GROUND = "#F4F4F6"
TILE = "#FFFFFF"
INK = "#0B0B0F"
MUTED = "#6E6E7A"
FAINT = "#9A9AA5"
HAIR = "#ECECF0"
VIOLET = "#5B4BFF"
VIOLET_SOFT = "#EEEBFF"
GREEN = "#15803D"
RED = "#DC2626"

STRATEGY = VIOLET          # Inverse-Vol series
BENCHMARK = "#A9A9B8"      # 60/40 series
ACCENT = VIOLET
LIGHT = "#D9D5FF"
GRID = "#EFEFF3"
BORDER = HAIR
NAVY = INK                 # kept for compatibility
ASSET_COLORS = {"SPY": "#22A3FF", "IEF": VIOLET, "GLD": "#F5A524", "SHY": "#D9D5FF"}
HEAT_SCALE = [[0, "#F4F3FF"], [0.5, "#A99FFF"], [1, VIOLET]]

_SHADOW = "0 1px 2px rgba(11,11,15,0.04), 0 6px 20px rgba(11,11,15,0.05)"

_CSS = f"""
<style>
html, body, [class*="st-"] {{ font-variant-numeric: tabular-nums; }}
::selection {{ background: {VIOLET_SOFT}; color: {INK}; }}
* {{ scrollbar-width: thin; scrollbar-color: #D4D4DC transparent; }}
[data-testid="stHeader"] {{ background: rgba(244,244,246,0.94); backdrop-filter: blur(8px); }}
.block-container {{ padding-top: 4.5rem; padding-bottom: 4rem; max-width: 1440px; }}
@media (max-width: 640px) {{ .modebar-container {{ display: none !important; }} .block-container {{ padding-top: 4.75rem !important; }} }}
:focus-visible {{ outline: 2px solid {VIOLET} !important; outline-offset: 2px; }}

/* ---------------- sidebar: white, pill navigation */
[data-testid="stSidebar"] {{ border-right: 1px solid {HAIR}; }}
[data-testid="stSidebarNavSeparator"] {{ border-color: {HAIR}; }}
[data-testid="stSidebarNav"] [data-testid="stNavSectionHeader"] {{
    color: {FAINT}; font-size: 0.74rem; font-weight: 700; letter-spacing: 0; text-transform: none; }}
[data-testid="stSidebarNav"] a {{ border-radius: 12px; padding-top: 0.15rem; padding-bottom: 0.15rem; }}
[data-testid="stSidebarNav"] a span {{ font-size: 0.88rem; font-weight: 600; color: #3A3A44; }}
[data-testid="stSidebarNav"] a[aria-current="page"] {{ background: {VIOLET_SOFT}; }}
[data-testid="stSidebarNav"] a[aria-current="page"] span {{ color: {VIOLET}; }}
[data-testid="stSidebarNav"] a:hover {{ background: #F4F4F6; }}
.sb-block {{ background: {GROUND}; border-radius: 16px; padding: 0.85rem 0.95rem; margin-top: 0.6rem; }}
.sb-label {{ color: {INK}; font-size: 0.8rem; font-weight: 700; margin-bottom: 0.4rem; }}
.sb-row {{ display: flex; justify-content: space-between; font-size: 0.8rem; padding: 0.2rem 0; color: {INK}; font-weight: 600; }}
.sb-row span:first-child {{ color: {MUTED}; font-weight: 500; }}
.sb-foot {{ color: {FAINT}; font-size: 0.74rem; line-height: 1.5; margin-top: 1.2rem; }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a {{ border-radius: 99px; background: {INK}; justify-content: center; }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a span, [data-testid="stSidebar"] [data-testid="stPageLink"] a p {{ color: #FFFFFF !important; font-weight: 700; }}

/* ---------------- page header */
.hdr {{ margin-bottom: 1.6rem; }}
.hdr-top {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 0.6rem 1rem; }}
.hdr h1 {{ word-break: normal !important; overflow-wrap: normal !important; font-size: clamp(1.6rem, 6vw, 2rem); font-weight: 800; color: {INK}; margin: 0; padding: 0; letter-spacing: -0.03em; line-height: 1.15; }}
.hdr .lede {{ color: {MUTED}; font-size: 0.92rem; margin: 0.45rem 0 0 0; max-width: 75ch; }}
.hdr .name {{ color: {FAINT}; font-size: 0.8rem; font-weight: 600; margin: 0.2rem 0 0 0; }}
.meta {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }}
.meta div {{ background: {TILE}; border-radius: 99px; padding: 0.45rem 0.9rem; box-shadow: 0 1px 2px rgba(11,11,15,0.04); font-size: 0.8rem; white-space: nowrap; }}
.meta span {{ color: {MUTED}; font-weight: 500; margin-right: 0.35rem; }}
.meta b {{ color: {INK}; font-weight: 700; }}
.status {{ font-size: 0.8rem; font-weight: 700; padding: 0.45rem 0.9rem; border-radius: 99px; white-space: nowrap; }}
.status.ok {{ color: {GREEN}; background: #E7F6EC; }}
.status.custom {{ color: #9A5B00; background: #FFF4DC; }}

/* ---------------- section titles and small text */
.sec {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 0.2rem 1rem; margin: 2rem 0 0.75rem 0; }}
.sec h3 {{ word-break: normal !important; overflow-wrap: normal !important; }}
.sec h3 {{ font-size: 1.3rem !important; letter-spacing: -0.01em; text-transform: none; color: {INK} !important; font-weight: 800 !important; margin: 0; padding: 0 !important; }}
.sec > span {{ color: {MUTED}; font-size: 0.82rem; font-weight: 500; }}
.panel-title {{ font-size: 1rem !important; font-weight: 800; color: {INK}; margin: 0; letter-spacing: -0.01em; }}
.panel-sub {{ font-size: 0.82rem !important; color: {MUTED}; margin: 0.15rem 0 0.4rem 0; }}
.note {{ color: {MUTED}; font-size: 0.8rem !important; line-height: 1.55; margin-top: 0.5rem; max-width: 110ch; }}
.fixed {{ font-size: 0.86rem !important; }}
.fixed div {{ display: flex; justify-content: space-between; gap: 1rem; border-bottom: 1px solid {HAIR}; padding: 0.55rem 0; }}
.fixed div:last-child {{ border-bottom: none; }}
.fixed div span:first-child {{ color: {MUTED}; }}
.fixed div span:last-child {{ color: {INK}; font-weight: 700; text-align: right; }}

/* ---------------- tiles: bordered containers become white rounded cards */
[data-testid="stVerticalBlock"][data-test-scroll-behavior] {{
    background: {TILE}; border: none !important; border-radius: 20px !important; box-shadow: {_SHADOW};
    padding: 1.3rem 1.4rem 1.1rem 1.4rem !important; }}

/* ---------------- KPI tiles (st.metric) */
[data-testid="stMetric"] {{
    background: {TILE}; border: none; border-radius: 20px; padding: 1.05rem 1.15rem 1rem 1.15rem;
    box-shadow: {_SHADOW}; height: 100%; }}
[data-testid="stMetricLabel"] p {{ font-size: 0.82rem !important; letter-spacing: 0; text-transform: none; color: {MUTED}; font-weight: 600; }}
[data-testid="stMetricValue"] {{ font-weight: 800; color: {INK}; letter-spacing: -0.02em; }}
[data-testid="stMetricDelta"] {{ font-size: 0.78rem; font-weight: 700; }}
/* the account card: last tile of a five-tile KPI row (Growth of $1) */
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"]):not(:has(> [data-testid="stColumn"]:nth-child(6)))
  > [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"] {{ background: {INK}; box-shadow: 0 8px 24px rgba(11,11,15,0.18); }}
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"]):not(:has(> [data-testid="stColumn"]:nth-child(6)))
  > [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"] :is([data-testid="stMetricLabel"] p, [data-testid="stMetricValue"]) {{ color: #FFFFFF !important; }}
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"]):not(:has(> [data-testid="stColumn"]:nth-child(6)))
  > [data-testid="stColumn"]:nth-child(5) [data-testid="stMetricLabel"] p {{ color: #B9B9C6 !important; }}
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"]):not(:has(> [data-testid="stColumn"]:nth-child(6)))
  > [data-testid="stColumn"]:nth-child(5) [data-testid="stMetricDelta"] {{ background: rgba(255,255,255,0.1); }}
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(5) [data-testid="stMetric"]):not(:has(> [data-testid="stColumn"]:nth-child(6)))
  > [data-testid="stColumn"]:nth-child(5) [data-testid="stMetricDelta"] :is(div, svg, p) {{ color: #D6D6E0 !important; fill: #D6D6E0; }}
/* narrow windows: shrink the numbers instead of cutting them off ("3....") */
[data-testid="stMetricValue"] {{ font-size: clamp(1.15rem, 1.8vw, 1.8rem) !important; }}
[data-testid="stMetricValue"] > div, [data-testid="stMetricDelta"] > div {{
    overflow: visible !important; text-overflow: clip !important; }}
[data-testid="stMetricLabel"] p, [data-testid="stMetricLabel"] div {{
    white-space: normal !important; overflow: visible !important; text-overflow: clip !important; }}
[data-testid="stMetricDelta"] > div {{ white-space: normal !important; }}
[data-testid="stMetricLabel"] p {{ word-break: normal !important; overflow-wrap: normal !important; }}
/* KPI rows wrap onto a second line instead of squeezing the tiles */
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] [data-testid="stMetric"]) {{ flex-wrap: wrap; row-gap: 0.85rem; }}
[data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"] [data-testid="stMetric"]) > [data-testid="stColumn"] {{ min-width: 150px !important; flex: 1 1 150px !important; }}
@media (max-width: 1200px) {{
    [data-testid="stMetric"] {{ padding: 0.85rem 0.8rem 0.8rem 0.8rem; }}
}}

/* ---------------- tables */
[data-testid="stTable"] {{ background: {TILE}; border-radius: 20px; box-shadow: {_SHADOW}; padding: 0.35rem 0.6rem; overflow: hidden; }}
[data-testid="stTable"] table {{ font-size: 0.86rem; border: none; }}
[data-testid="stTable"] th, [data-testid="stTable"] td {{ border: none !important; border-bottom: 1px solid {HAIR} !important; }}
[data-testid="stTable"] tr:last-child td, [data-testid="stTable"] tr:last-child th {{ border-bottom: none !important; }}
[data-testid="stTable"] thead th {{ color: {MUTED}; font-weight: 600; }}
[data-testid="stTable"] tbody th {{ color: {INK}; font-weight: 700; }}
[data-testid="stDataFrame"] {{ background: {TILE}; border-radius: 20px; box-shadow: {_SHADOW}; padding: 0.4rem; }}

/* ---------------- controls */
[data-testid="stButton"] button, [data-testid="stDownloadButton"] button {{ border-radius: 99px; font-weight: 700; }}
[data-testid="stDownloadButton"] button {{ background: {INK}; color: #FFFFFF; border: none; }}
[data-testid="stDownloadButton"] button:hover {{ background: #2A2A33; color: #FFFFFF; }}
[data-testid="stWidgetLabel"] p {{ font-weight: 600; color: {INK}; }}
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
  <div class="hdr-top"><h1>{escape(title)}</h1>{status}</div>
  <p class="lede">{escape(lede)}</p>
  <p class="name">IVS · Inverse Volatility Strategy</p>
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
    """Money-app chart styling: no frame, faint horizontal guides, rounded bars."""
    fig.update_layout(
        height=height, template="none", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope, Segoe UI, Arial, sans-serif", size=12, color=MUTED),
        margin=dict(l=4, r=4, t=8, b=4), hovermode="x unified", title=None, barcornerradius=4,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                    font=dict(size=12, color=INK), title=None, bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=INK, bordercolor=INK, font=dict(color="#FFFFFF", size=12,
                                                                   family="Manrope, Segoe UI, sans-serif")),
    )
    fig.update_xaxes(showgrid=False, showline=False, ticks="", title=None,
                     showspikes=True, spikemode="across", spikethickness=1, spikecolor="#C9C9D3",
                     spikedash="solid")
    fig.update_yaxes(gridcolor=GRID, griddash="dot", zeroline=False, showline=False, ticks="", title=None)
    if pct_axis:
        fig.update_yaxes(tickformat=".0%")
    return fig
