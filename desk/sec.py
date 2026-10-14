"""SEC EDGAR filings (free). The SEC requires a User-Agent with a contact email: env SEC_USER_AGENT,
e.g. "options-desk you@example.com". Allowed hosts needed: www.sec.gov, data.sec.gov.

Forms that matter for a trade:
  8-K      material events (exec changes, guidance, deals, offerings)
  10-Q/10-K  quarterly/annual report
  4        insider buy/sell (open-market BUYS by several insiders are the useful signal)
  DEF 14A  proxy: shareholder meeting agenda and votes
  SC 13D/13G  activist / large holder stakes
  S-3, 424B*  share offerings (dilution)
"""
import datetime as dt, os
from .http import get_json

WATCH_FORMS = {"8-K", "10-Q", "10-K", "4", "DEF 14A", "DEFA14A", "SC 13D", "SC 13D/A", "SC 13G",
               "SC 13G/A", "S-3", "424B5", "424B3"}

def _ua():
    ua = os.environ.get("SEC_USER_AGENT")
    if not ua:
        raise RuntimeError("set SEC_USER_AGENT (name + contact email) in the environment settings")
    return {"User-Agent": ua, "Accept-Encoding": "identity"}

_cik_cache = {}

def cik(ticker):
    t = ticker.upper()
    if not _cik_cache:
        data = get_json("https://www.sec.gov/files/company_tickers.json", _ua())
        for row in data.values():
            _cik_cache[row["ticker"].upper()] = int(row["cik_str"])
    if t not in _cik_cache:
        raise KeyError(f"{t} not found in SEC ticker list (ETFs and funds aren't there)")
    return _cik_cache[t]

def recent_filings(ticker, days=30, forms=WATCH_FORMS, today=None):
    c = cik(ticker)
    data = get_json(f"https://data.sec.gov/submissions/CIK{c:010d}.json", _ua())
    rec = data["filings"]["recent"]
    since = (today or dt.date.today()) - dt.timedelta(days=days)
    out = []
    for form, date, acc, doc, items in zip(rec["form"], rec["filingDate"], rec["accessionNumber"],
                                           rec["primaryDocument"], rec.get("items", [""] * len(rec["form"]))):
        if dt.date.fromisoformat(date) < since or (forms and form not in forms):
            continue
        url = f"https://www.sec.gov/Archives/edgar/data/{c}/{acc.replace('-', '')}/{doc}"
        out.append({"form": form, "date": date, "items": items, "url": url})
    return out

# 8-K item numbers -> plain words (the ones that move stocks)
ITEMS_8K = {"1.01": "material agreement", "1.03": "bankruptcy", "2.02": "earnings results",
            "2.05": "restructuring/layoffs", "2.06": "impairment", "3.01": "delisting notice",
            "4.02": "restated financials", "5.02": "exec/director change", "5.07": "shareholder vote results",
            "7.01": "Reg FD disclosure", "8.01": "other events"}

def describe(f):
    if f["form"] == "8-K" and f["items"]:
        words = [ITEMS_8K.get(i.strip(), i.strip()) for i in f["items"].split(",")]
        return f"8-K: {', '.join(words)}"
    return f["form"]
