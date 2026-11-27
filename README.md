# DIVMA: Dynamic Inverse Volatility Multi-Asset Strategy (Streamlit app)

2270 Financial Modeling, group assignment (Group BD).
Team: Alberto (data), Beatriz (backtest engine), Margarida (metrics), Rodrigo and Francisco (prospectus), Yuling (app and QA).

An interactive backtest of a monthly-rebalanced inverse-volatility (risk parity) portfolio
of SPY, IEF, GLD and SHY, compared with a 60/40 SPY/IEF benchmark. Prices come from the
Yahoo Finance chart API and the risk-free rate from FRED (DGS3MO); the app reads no local data files.

**Live app:** <add Streamlit Cloud URL after deployment>  ·  **Repository:** https://github.com/Shenu-Fin/Group-BD---Financial-Modeling-Project

## What you can change
Volatility lookback · transaction costs (bps) · rebalancing frequency (monthly, quarterly, annual) ·
whether costs also apply to the 60/40 benchmark.
At the baseline settings (`config.py`), the results match the group notebook and the PDF.

## Project structure
| File | Purpose |
|---|---|
| `config.py` | Baseline parameters: the single source of truth shared with the notebook |
| `data.py` | Part 1 data pipeline: Yahoo adjusted closes (NYSE-calendar checked) and the FRED risk-free rate |
| `engine.py` | Part 2 backtest engine: inverse-vol weights at each month-end, held the next month; drift, turnover, costs |
| `metrics.py` | Ann. average return, volatility, Sharpe, non-annualised Beta, Jensen's Alpha, IR, Max DD |
| `app.py` | Streamlit user interface: sidebar pages (Overview, Performance, Allocation, Risk & Drawdown, Transaction Costs, Sensitivity Analysis, Methodology) |
| `ui.py` | Presentation helpers: palette, CSS, page header, chart styling (no calculations) |
| `.streamlit/config.toml`, `assets/` | Theme (navy / white / muted blue) and sidebar logo |
| `tests/` | Offline tests, including a look-ahead test (`pytest -q`) |

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
pytest -q          # optional checks
```

## Deploy
share.streamlit.io → Create app → repo `Shenu-Fin/Group-BD---Financial-Modeling-Project`, branch `main`, main file `app.py`.
In Advanced settings choose Python 3.12 (pandas 3 needs Python 3.11 or newer).

## Status
- `data.py`, `engine.py`: ported from the group notebook (Parts 1 and 2); results verified identical.
- `metrics.py`: ported from the group notebook (Part 3); performance table verified identical.

*Educational project. Not investment advice.*
