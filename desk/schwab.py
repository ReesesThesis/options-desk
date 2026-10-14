"""Schwab Trader API (market data only; we never send orders).

Environment variables (set in the cloud environment settings, never in chat or files):
  SCHWAB_APP_KEY, SCHWAB_APP_SECRET, SCHWAB_REFRESH_TOKEN
  SCHWAB_REFRESH_ISSUED   date the refresh token was made (YYYY-MM-DD); Schwab refresh tokens
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

def refresh_days_left(today=None):
    issued = os.environ.get("SCHWAB_REFRESH_ISSUED")
    if not issued:
        return None
    return REFRESH_DAYS - ((today or dt.date.today()) - dt.date.fromisoformat(issued)).days

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
