"""Build the pre-registered entry-date signals for PHASE1_FINAL.md.

    python3 backtests/make_signals.py backtests/data/SPY.csv backtests/data/KO.csv backtests/data/VIX_History.csv

Reads daily price CSVs (Nasdaq.com "Close/Last" or plain "Close"; Cboe VIX "CLOSE"; dates as
YYYY-MM-DD or MM/DD/YYYY) and writes backtests/signals/<RUN>_dates.csv with one date per line.
Every signal for day D uses only closes up to D-1 (entries are at 10:00 on D).
Output follows ORATS's intraday signal template (owner's download, 2026-10-16): columns
"entry","exit", each YYYYMMDDHHMM. Exit = 16:00 on the last trading day within 30 calendar days of
entry, i.e. no earlier than a 30-DTE expiration, so ORATS's own exits (profit target, expiration)
should come first. Whether ORATS treats each row as its own (overlapping) trade is checked with
signals/PROBE_SPY.csv before the real runs.
"""
import csv, datetime as dt, os, statistics, sys

START, END = dt.date(2020, 10, 1), dt.date.today()

def load(path):
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8-sig")))
    keys = {k.strip().lower(): k for k in rows[0]}
    dk = keys.get("date")
    ck = next(keys[k] for k in ("close/last", "close", "adj close") if k in keys)
    out = {}
    for r in rows:
        s = r[dk].strip()
        d = dt.datetime.strptime(s, "%m/%d/%Y").date() if "/" in s else dt.date.fromisoformat(s)
        out[d] = float(r[ck].replace("$", "").replace(",", ""))
    return sorted(out.items())

def trend_dates(series, n=50):
    """Day D qualifies if close(D-1) > mean of the 50 closes ending D-1."""
    days = [d for d, _ in series]; closes = [c for _, c in series]
    out = []
    for i in range(n, len(series)):
        prev = closes[i - n:i]
        if closes[i - 1] > sum(prev) / n:
            out.append(days[i])
    return out

def vol_dates(vix, n=252):
    """Day D qualifies if VIX close(D-1) > median of the 252 closes before D-1."""
    days = [d for d, _ in vix]; closes = [c for _, c in vix]
    out = []
    for i in range(n + 1, len(vix)):
        if closes[i - 1] > statistics.median(closes[i - 1 - n:i - 1]):
            out.append(days[i])
    return out

def keep(dates, trading_days):
    return [d for d in dates if START <= d <= END and d in trading_days]

HOLD_DAYS = 30

def stamp(d, hhmm):
    return d.strftime("%Y%m%d") + hhmm

def exit_day(d, trading_days, hold=HOLD_DAYS):
    """Last trading day on or before d + hold calendar days."""
    x = d + dt.timedelta(days=hold)
    while x not in trading_days:
        x -= dt.timedelta(days=1)
    return x

def rows(dates, trading_days):
    return [(stamp(d, "1000"), stamp(exit_day(d, trading_days), "1600")) for d in dates]

def write(name, dates, trading_days):
    os.makedirs(os.path.join(os.path.dirname(__file__), "signals"), exist_ok=True)
    path = os.path.join(os.path.dirname(__file__), "signals", f"{name}.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["entry", "exit"]); w.writerows(rows(dates, trading_days))
    print(f"{name}: {len(dates)} entry days -> {path}")

if __name__ == "__main__":
    spy, ko, vix = (load(p) for p in sys.argv[1:4])
    spy_days, ko_days = {d for d, _ in spy}, {d for d, _ in ko}
    v = vol_dates(vix)
    write("F1_SPY_trend", keep(trend_dates(spy), spy_days), spy_days)
    write("F2_SPY_vol", keep(v, spy_days), spy_days)
    write("F3_KO_trend", keep(trend_dates(ko), ko_days), ko_days)
    write("F4_KO_vol", keep(v, ko_days), ko_days)
