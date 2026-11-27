# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
The professor and graders of course 2270 Financial Modeling. They open the app to assess Group BD's project: confirm that the baseline results match the group notebook and the written prospectus, and change a few assumptions to see how the strategy responds.

## Product Purpose
IVS is an interactive backtest of a monthly-rebalanced inverse-volatility (risk parity) portfolio of SPY, IEF, GLD and SHY, compared with a 60/40 SPY/IEF benchmark (Mar 2005 – Oct 2026). Success means a grader can verify the figures quickly, trust that they match the prospectus, and explore the assumptions without help.

## Positioning
The app runs the group notebook's own code (data, engine, metrics) live, so every number on screen is reproducible from the notebook at baseline settings, and every assumption change re-runs the full backtest.

## Operating Context
Opened in a desktop browser from the Streamlit Community Cloud link, deployed from GitHub `main` of Shenu-Fin/Group-BD---Financial-Modeling-Project. Read alongside the group notebook and the PDF prospectus.

## Capabilities and Constraints
- Streamlit (1.67) + Plotly; hosted on Streamlit Community Cloud from GitHub `main`. Must keep deploying there.
- Seven pages: Overview, Performance, Allocation, Risk & Drawdown, Transaction Costs, Sensitivity Analysis, Methodology.
- Editable assumptions: volatility lookback, transaction cost, rebalancing frequency, costs on the benchmark, log scale.
- Fixed: all figures and all calculation code (`data.py`, `engine.py`, `metrics.py`, `config.py`, and the calculations in `app.py`). Visual changes only.
- Fixed: on-page wording (labels, captions, methodology text) stays word for word.

## Brand Commitments
Name: IVS (Inverse Volatility Strategy), Group BD, 2270 Financial Modeling. Disclaimer "Educational project. Not investment advice." must remain.

## Evidence on Hand
Live market data (Yahoo Finance, FRED DGS3MO) computed at runtime. No testimonials, users or external claims exist; none may be invented.

## Product Principles
1. Numbers first: every figure is traceable to the notebook and must stay exact.
2. Verification is fast: baseline status and the reporting period are always visible.
3. Honest comparison: strategy and benchmark are always shown on equal footing, gross and net labelled.
4. Academic integrity: no invented data, claims or advice.
