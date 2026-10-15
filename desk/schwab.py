"""Schwab Trader API (market data only; we never send orders).

Environment variables (set in the cloud environment settings, never in chat or files):
  SCHWAB_APP_KEY, SCHWAB_APP_SECRET, SCHWAB_REFRESH_TOKEN
  SCHWAB_REFRESH_ISSUED   date the refresh token was made (YYYY-MM-DD, or MMDDYYYY); Schwab refresh tokens
                          last 7 days, so the brief warns a day before it runs out.
Allowed host needed: api.schwabapi.com

First sign-in (once a week, on your own computer): python3 -m desk.schwab_login
"""
import base64, datetime as dt, os
from .http import get_json, post_form

BASE = "https://api.schwabapi.com"
REFRESH_DAYS = 7
_token = None

def _env(k):
    v = os.environ.get(k)
    if not v:
        raise RuntimeError(f"{k} is not set in the environment settings")
    return v

def basic_auth():
    raw = f"{_env('SCHWAB_APP_KEY')}:{_env('SCHWAB_APP_SECRET')}".encode()
    return {"Authorization": "Basic " + base64.b64encode(raw).decode(),
            "Content-Type": "application/x-www-form-urlencoded"}

def parse_issued(s):
    """YYYY-MM-DD, or MMDDYYYY as typed in the environment settings (10152026)."""
    s = s.strip()
    if len(s) == 8 and s.isdigit() and not s.startswith(("19", "20")):
        return dt.date(int(s[4:]), int(s[:2]), int(s[2:4]))
    return dt.date.fromisoformat(s)

def refresh_days_left(today=None):
    issued = os.environ.get("SCHWAB_REFRESH_ISSUED")
    if not issued:
        return None
    return REFRESH_DAYS - ((today or dt.date.today()) - parse_issued(issued)).days

def access_token():
    global _token
    if _token is None:
        r = post_form(f"{BASE}/v1/oauth/token",
                      {"grant_type": "refresh_token", "refresh_token": _env("SCHWAB_REFRESH_TOKEN")},
                      basic_auth())
        _token = r["access_token"]
    return _token

def _get(path, params):
    return get_json(BASE + path, {"Authorization": f"Bearer {access_token()}"}, params)

def quote(symbol):
    d = _get("/marketdata/v1/quotes", {"symbols": symbol.upper()})
    return d[symbol.upper()]["quote"]

def daily_closes(symbol, years=1):
    d = _get("/marketdata/v1/pricehistory", {"symbol": symbol.upper(), "periodType": "year",
                                              "period": years, "frequencyType": "daily", "frequency": 1})
    return [(dt.datetime.fromtimestamp(c["datetime"] / 1000).date(), c["close"]) for c in d["candles"]]

def daily_bars(symbol, start, end=None):
    """Daily OHLCV from start (date) to end (default today); dates are the trading day."""
    ms = lambda d: int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() * 1000)
    end = end or dt.date.today() + dt.timedelta(days=1)
    d = _get("/marketdata/v1/pricehistory", {"symbol": symbol.upper(), "periodType": "year",
                                              "frequencyType": "daily", "frequency": 1,
                                              "startDate": ms(start), "endDate": ms(end)})
    # candles are stamped at midnight US Eastern (04:00/05:00 UTC); +6 h lands on the trading day
    return [{"date": (dt.datetime.fromtimestamp(c["datetime"] / 1000, dt.timezone.utc) + dt.timedelta(hours=6)).date(),
             "open": c["open"], "high": c["high"], "low": c["low"], "close": c["close"],
             "volume": c["volume"]} for c in d.get("candles", [])]

def chain(symbol, from_date=None, to_date=None, strike_count=30):
    """Option chain normalized to a flat list of contracts."""
    params = {"symbol": symbol.upper(), "contractType": "ALL", "strikeCount": strike_count,
              "includeUnderlyingQuote": "true"}
    if from_date:
        params["fromDate"] = str(from_date)
    if to_date:
        params["toDate"] = str(to_date)
    d = _get("/marketdata/v1/chains", params)
    return {"spot": d.get("underlyingPrice"), "contracts": normalize(d)}

def normalize(d):
    out = []
    for kind, key in (("call", "callExpDateMap"), ("put", "putExpDateMap")):
        for exp_key, strikes in (d.get(key) or {}).items():
            expiry = exp_key.split(":")[0]
            for strike, rows in strikes.items():
                for c in rows:
                    iv = c.get("volatility")
                    out.append({"type": kind, "expiry": expiry, "strike": float(strike),
                                "bid": c.get("bid"), "ask": c.get("ask"), "mark": c.get("mark"),
                                "iv": iv / 100 if isinstance(iv, (int, float)) and iv > 0 else None,
                                "delta": c.get("delta"), "gamma": c.get("gamma"), "theta": c.get("theta"),
                                "vega": c.get("vega"), "oi": c.get("openInterest"),
                                "volume": c.get("totalVolume"), "symbol": c.get("symbol")})
    return out
