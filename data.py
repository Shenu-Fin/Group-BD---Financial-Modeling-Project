"""
data.py: Part 1's data pipeline (Person 1), ported from the group notebook.

Functions are copied from notebook cells 1.2 and 1.3, with only the global
constants replaced by `config`. Do not change the logic here without
changing the notebook too, or the app will stop matching the prospectus.
"""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from time import sleep
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

import numpy as np
import pandas as pd
import pandas_market_calendars as mcal

import config as C


# ---------------------------------------------------------------- 1.2 Yahoo prices
def read_url(url, timeout=25):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=timeout) as response:
        return response.read()


def download_etf(ticker):
    query = urlencode({
        "period1": int(C.PRICE_START.tz_localize("UTC").timestamp()),
        "period2": int((C.SAMPLE_END + pd.Timedelta(days=1)).tz_localize("UTC").timestamp()),
        "interval": "1d",
        "events": "history",
        "includeAdjustedClose": "true",
    })
    errors = []
    for attempt in range(2):
        for host in C.YAHOO_HOSTS:
            url = f"https://{host}/v8/finance/chart/{ticker}?{query}"
            try:
                chart = json.loads(read_url(url))["chart"]
                if chart["error"] or not chart["result"]:
                    raise ValueError(f"Yahoo chart error: {chart['error']}")
                data = chart["result"][0]
                meta = data["meta"]
                if meta["symbol"] != ticker or meta["currency"] != "USD":
                    raise ValueError(f"Unexpected symbol or currency: {meta['symbol']}, {meta['currency']}")
                index = (
                    pd.to_datetime(data["timestamp"], unit="s", utc=True)
                    .tz_convert(meta["exchangeTimezoneName"])
                    .tz_localize(None)
                    .normalize()
                    .rename("Date")
                )
                prices = pd.DataFrame({
                    "Close": data["indicators"]["quote"][0]["close"],
                    "Adj Close": data["indicators"]["adjclose"][0]["adjclose"],
                }, index=index, dtype=float)
                return prices, url
            except (OSError, ValueError, KeyError, IndexError) as exc:
                errors.append(f"{host}: {exc}")
        if attempt == 0:
            sleep(2)
    raise RuntimeError(f"Yahoo Finance could not supply {ticker}: {' | '.join(errors)}")


def load_adjusted_close() -> pd.DataFrame:
    """Validated daily adjusted closes (notebook variable `adjusted_close`)."""
    with ThreadPoolExecutor(max_workers=len(C.TICKERS)) as pool:
        downloads = dict(zip(C.TICKERS, pool.map(download_etf, C.TICKERS)))

    sessions = mcal.get_calendar("NYSE").schedule(
        start_date=C.PRICE_START, end_date=C.SAMPLE_END
    ).index.normalize().rename("Date")
    for ticker, (prices, _) in downloads.items():
        if not prices.index.is_unique or not prices.index.is_monotonic_increasing:
            raise ValueError(f"{ticker}: duplicate or out-of-order dates")
        missing = sessions.difference(prices.index)
        extra = prices.index.difference(sessions)
        if len(missing) or len(extra):
            raise ValueError(f"{ticker}: missing sessions {list(missing[:8])}, extra dates {list(extra[:8])}")
        if not np.isfinite(prices.to_numpy()).all() or not prices.gt(0).all().all():
            raise ValueError(f"{ticker}: missing, non-finite or non-positive close")

    return pd.DataFrame({t: p["Adj Close"] for t, (p, _) in downloads.items()})


# ---------------------------------------------------------------- 1.3 risk-free rate
def read_fred(url):
    # FRED sometimes rejects generic browser headers used by market-data feeds.
    request = Request(url, headers={"User-Agent": "curl/8.12.1", "Accept": "*/*"})
    with urlopen(request, timeout=20) as response:
        return response.read()


def download_risk_free_yield():
    bounded_query = urlencode({
        "id": C.FRED_SERIES, "cosd": (C.PRICE_START - pd.Timedelta(days=1)).date(),
        "coed": C.SAMPLE_END.date()
    })
    ddp_query = urlencode({
        "rel": "H15", "series": "bf17364827e38702b42a58cf8eaa3f78",
        "lastobs": "", "from": "", "to": "", "filetype": "csv",
        "label": "include", "layout": "seriescolumn", "type": "package",
    })
    feeds = [
        (f"{C.FRED_URL}?{bounded_query}", C.FRED_SERIES, 0),
        (f"{C.FRED_URL}?id={C.FRED_SERIES}", C.FRED_SERIES, 0),
        (f"{C.FED_DDP_URL}?{ddp_query}", C.FED_DDP_SERIES, 5),
    ]
    errors = []
    for url, column, skiprows in feeds:
        try:
            data = pd.read_csv(BytesIO(read_fred(url)), skiprows=skiprows, na_values=[".", "ND"])
            dates = pd.to_datetime(data.iloc[:, 0], errors="raise")
            values = pd.to_numeric(data[column], errors="raise")
            series = pd.Series(values.to_numpy(), index=dates, name="annual_yield_pct").sort_index()
            series = series.loc[C.PRICE_START:C.SAMPLE_END].dropna()
            if (not series.index.is_unique or series.empty or not np.isfinite(series).all()
                    or series.index[0] > C.BASE_DATE or (C.SAMPLE_END - series.index[-1]).days > 7):
                raise ValueError("The yield series has incomplete or invalid coverage")
            return series, url
        except (OSError, ValueError, KeyError) as exc:
            errors.append(str(exc))
    raise RuntimeError(f"FRED and H.15 could not supply complete {C.FRED_SERIES} data: {' | '.join(errors)}")


def load_risk_free_daily(eval_index: pd.DatetimeIndex) -> pd.Series:
    """Daily rf on each evaluation date, using the latest yield dated STRICTLY earlier,
    divided by 100 and 252 (notebook variable `risk_free_daily`)."""
    risk_free_yield, _ = download_risk_free_yield()
    pos = risk_free_yield.index.searchsorted(eval_index, side="left") - 1
    assert (pos >= 0).all()
    return pd.Series(risk_free_yield.iloc[pos].to_numpy() / 100 / C.TRADING_DAYS,
                     index=eval_index, name="RF")


def load_all():
    """Everything the app needs, exactly as in the notebook."""
    adjusted_close = load_adjusted_close()
    asset_returns = adjusted_close.pct_change(fill_method=None).iloc[1:].loc[C.SAMPLE_START:C.SAMPLE_END]
    risk_free_daily = load_risk_free_daily(asset_returns.index)
    return adjusted_close, risk_free_daily
