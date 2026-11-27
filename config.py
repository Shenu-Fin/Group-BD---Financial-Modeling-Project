"""
config.py: baseline parameters, copied from the group notebook (Part 1, cell 1.1).

At these values the app must reproduce the notebook and the prospectus exactly.
If the notebook changes, change this file too.
"""
import pandas as pd

TICKERS = ("SPY", "IEF", "GLD", "SHY")
PRICE_START = pd.Timestamp("2004-11-18")   # GLD inception; supplies the 60-day warm-up
BASE_DATE = pd.Timestamp("2005-02-28")     # common base close (value = 1) and first signal
SAMPLE_START = pd.Timestamp("2005-03-01")
SAMPLE_END = pd.Timestamp("2026-10-30")
TRADING_DAYS = 252
LOOKBACK = 60
REBALANCE_COST_BPS = 10
BENCHMARK_TARGET = pd.Series({"SPY": 0.60, "IEF": 0.40})
REBAL_FREQ = "Monthly"

# Risk-free rate: FRED 3-month constant-maturity Treasury yield (Part 1, cell 1.3)
FRED_SERIES = "DGS3MO"
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
FED_DDP_URL = "https://www.federalreserve.gov/datadownload/Output.aspx"
FED_DDP_SERIES = "RIFLGFCM03_N.B"
YAHOO_HOSTS = ("query1.finance.yahoo.com", "query2.finance.yahoo.com")
