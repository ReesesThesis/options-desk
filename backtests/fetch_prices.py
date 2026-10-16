"""Daily price history from Schwab into backtests/data/<SYMBOL>.csv (Date,Open,High,Low,Close,Volume).

    python3 backtests/fetch_prices.py                     # default list below, since 2019-01-01
    python3 backtests/fetch_prices.py KO SPY --since 2019-01-01
    python3 backtests/fetch_prices.py $(grep -v '^#' backtests/universe_large.txt) --since 2018-01-01 --out backtests/data/stocks

Schwab's prices are split-adjusted, not dividend-adjusted (closes match what a chart shows), which
is what the 50-day trend filter needs. $VIX is cut to the days SPY traded: Schwab also has VIX bars
on some market holidays (2025-07-04, Thanksgiving, ...), and the V filter counts trading days. Writes a summary line per symbol: rows, first/last date,
largest one-day move, so a missing day or an unadjusted split stands out.
"""
import argparse, csv, datetime as dt, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from desk import schwab

DEFAULT = ["SPY", "KO", "XLU", "XLF", "XLE", "XLK", "XLV", "XLP", "XLI", "XLY", "XLB", "XLRE", "XLC", "$VIX"]
OUT = os.path.join(os.path.dirname(__file__), "data")

def write(symbol, bars, out_dir=OUT):
    os.makedirs(out_dir, exist_ok=True)
    name = symbol.lstrip("$").upper().replace("/", ".") + ".csv"
    path = os.path.join(out_dir, name)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        for b in bars:
            w.writerow([b["date"].isoformat(), b["open"], b["high"], b["low"], b["close"], b["volume"]])
    return path

def check(bars):
    """Duplicate dates and the largest close-to-close move (a 2-for-1 split shows as about -50%)."""
    dates = [b["date"] for b in bars]
    dupes = len(dates) - len(set(dates))
    big = max(((bars[i]["close"] / bars[i - 1]["close"] - 1, bars[i]["date"]) for i in range(1, len(bars))),
              key=lambda x: abs(x[0]))
    return dupes, big

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("symbols", nargs="*", default=DEFAULT)
    ap.add_argument("--since", default="2019-01-01")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    since = dt.date.fromisoformat(a.since)
    spy_days = None
    for s in sorted(a.symbols, key=lambda s: s != "SPY"):
        try:
            bars = [b for b in schwab.daily_bars(s, since) if b["date"] >= since]
        except Exception as e:
            print(f"{s:6} FAILED: {e}"); continue
        if s == "SPY":
            spy_days = {b["date"] for b in bars}
        elif s.startswith("$") and spy_days:
            extra = [b["date"] for b in bars if b["date"] not in spy_days]
            bars = [b for b in bars if b["date"] in spy_days]
            missing = sorted(spy_days - {b["date"] for b in bars})
            print(f"{s:6} dropped {len(extra)} non-trading days; missing trading days: {missing or 'none'}")
        if not bars:
            print(f"{s:6} NO DATA"); continue
        path = write(s, bars, a.out)
        dupes, (move, day) = check(bars)
        print(f"{s:6} {len(bars):5} rows  {bars[0]['date']} .. {bars[-1]['date']}  last close {bars[-1]['close']:.2f}"
              f"  biggest day {move:+.1%} on {day}{'  DUPLICATE DATES: %d' % dupes if dupes else ''}  -> {os.path.relpath(path)}")

if __name__ == "__main__":
    main()
