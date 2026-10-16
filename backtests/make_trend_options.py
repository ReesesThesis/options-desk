"""Signals for the owner's directional test (pre-registered in PHASE1_TREND_OPTIONS.md).

    python3 backtests/make_trend_options.py backtests/data/SPY.csv

Weekly, on the first trading day D of each week, at 10:00:
  T1 (long call): if SPY's close on D-1 is ABOVE its 50-day average (50 closes ending D-1)
  T2 (long put):  if it is BELOW
Exit: 10:00 on the first day whose prior close is on the other side of the average (trend flipped),
or 16:00 on the last trading day within 21 calendar days of entry, whichever comes first.
Writes backtests/signals/T1_SPY_call.csv and T2_SPY_put.csv in ORATS's entry,exit format.
"""
import datetime as dt, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_signals as ms

TIME_STOP = 21

def sides(series, n=50):
    """{day D: +1 if close(D-1) > SMA50 ending D-1, -1 if below, 0 if equal}."""
    days = [d for d, _ in series]; closes = [c for _, c in series]
    out = {}
    for i in range(n, len(series)):
        avg = sum(closes[i - n:i]) / n
        out[days[i]] = (closes[i - 1] > avg) - (closes[i - 1] < avg)
    return out

def week_starts(days):
    seen, out = set(), []
    for d in sorted(days):
        wk = d.isocalendar()[:2]
        if wk not in seen:
            seen.add(wk); out.append(d)
    return out

def trades(series, want):
    """Entry/exit stamps for side want (+1 call, -1 put)."""
    side = sides(series)
    days = sorted(side)
    tset = set(d for d, _ in series)
    last = min(ms.END, max(tset)) - dt.timedelta(days=ms.HOLD_DAYS)
    out = []
    for d in week_starts(days):
        if not (ms.START <= d <= last) or side[d] != want:
            continue
        stop = ms.exit_day(d, tset, TIME_STOP)
        flip = next((e for e in days if d < e <= stop and side[e] == -want), None)
        out.append((ms.stamp(d, "1000"), ms.stamp(flip, "1000") if flip else ms.stamp(stop, "1600")))
    return out

def write(name, rows):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signals", f"{name}.csv")
    with open(path, "w") as f:
        f.write("entry,exit\n" + "".join(f"{a},{b}\n" for a, b in rows))
    print(f"{name}: {len(rows)} trades -> {path}")

if __name__ == "__main__":
    spy = ms.load(sys.argv[1])
    write("T1_SPY_call", trades(spy, +1))
    write("T2_SPY_put", trades(spy, -1))
