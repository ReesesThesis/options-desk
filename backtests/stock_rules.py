"""The three pre-registered stock rules in STOCK_RULES.md, run on Schwab daily prices.

    python3 backtests/stock_rules.py

Decisions at the close of day D, trades at the open of D+1, 0.05% cost on every amount traded,
cash at 0%. Calendar = SPY's trading days in backtests/data/SPY.csv (through 2026-10-15).
"""
import csv, datetime as dt, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))
COST = 0.0005
H1_END = dt.date(2022, 12, 31)
SECTORS = "XLB XLC XLE XLF XLI XLK XLP XLRE XLU XLV XLY".split()

def load(path):
    out = {}
    for r in csv.DictReader(open(path)):
        out[dt.date.fromisoformat(r["Date"])] = (float(r["Open"]), float(r["Close"]))
    return out

def load_all():
    px = {os.path.basename(p)[:-4]: load(p) for p in glob.glob(os.path.join(HERE, "data", "*.csv"))}
    stocks = {os.path.basename(p)[:-4]: load(p) for p in glob.glob(os.path.join(HERE, "data", "stocks", "*.csv"))}
    return px, stocks

def simulate(cal, prices, decide):
    """decide(i) -> dict of target weights (or None = keep), using closes up to cal[i].
    Returns (dates, values, trades) with values marked at each close from the first fill."""
    cash, shares, pending, started = 1.0, {}, None, False
    dates, values, trades = [], [], 0
    last_close = {}
    for i, d in enumerate(cal):
        for s, p in prices.items():
            if d in p:
                last_close[s] = p[d][1]
        if pending is not None and "_sell" in pending:
            # sell only these holdings to cash; leave the rest untouched (stop-outs)
            for s in pending["_sell"]:
                if s in shares:
                    px_open = prices[s][d][0] if d in prices[s] else last_close[s]
                    cash += shares.pop(s) * px_open * (1 - COST)
                    trades += 1
            pending = None
        if pending is not None:
            opens = {s: prices[s][d][0] if d in prices[s] else last_close[s] for s in set(shares) | set(pending)}
            value = cash + sum(n * opens[s] for s, n in shares.items())
            new = {s: value * w / opens[s] for s, w in pending.items() if w > 0}
            traded = sum(abs(new.get(s, 0) - shares.get(s, 0)) * opens[s] for s in set(new) | set(shares))
            trades += sum(1 for s in set(new) | set(shares) if abs(new.get(s, 0) - shares.get(s, 0)) * opens[s] > 1e-9)
            shares = new
            cash = value - sum(n * opens[s] for s, n in shares.items()) - traded * COST
            pending, started = None, True
        if started:
            dates.append(d)
            values.append(cash + sum(n * last_close[s] for s, n in shares.items()))
        t = decide(i)
        if t is not None:
            pending = t
    return dates, values, trades

def month_ends(cal):
    return {cal[i] for i in range(len(cal) - 1) if cal[i + 1].month != cal[i].month}

def closes_upto(p, d, n):
    """The last n closes on or before d, oldest first (fewer if history is short)."""
    ks = [k for k in p if k <= d]
    ks.sort()
    return [p[k][1] for k in ks[-n:]]

# ---- rules -------------------------------------------------------------------------------

def s1(cal, px):
    spy = px["SPY"]; state = {"on": None}
    def decide(i):
        c = closes_upto(spy, cal[i], 200)
        if len(c) < 200:
            return None
        on = c[-1] > sum(c) / 200
        if on == state["on"]:
            return None
        state["on"] = on
        return {"SPY": 1.0} if on else {}
    return decide

def s2(cal, px):
    me = month_ends(cal)
    def decide(i):
        if cal[i] not in me:
            return None
        rets = {}
        for s in SECTORS:
            c = closes_upto(px[s], cal[i], 64)
            if len(c) == 64:
                rets[s] = c[-1] / c[0] - 1
        if len(rets) < 3:
            return None
        top = sorted(rets, key=rets.get, reverse=True)[:3]
        return {s: 1 / 3 for s in top}
    return decide

def eligible(stocks, d):
    out = {}
    for s, p in stocks.items():
        c = closes_upto(p, d, 273)
        if len(c) == 273:
            out[s] = c
    return out

def s3(cal, stocks, top_n=5):
    me = month_ends(cal)
    def decide(i):
        if cal[i] not in me:
            return None
        el = eligible(stocks, cal[i])
        if len(el) < top_n:
            return None
        # 12-1 momentum: c[-1] is today, so c[-22] is 21 trading days ago and c[-253] is 252 days ago
        mom = {s: c[-22] / c[-253] - 1 for s, c in el.items()}
        top = sorted(mom, key=mom.get, reverse=True)[:top_n]
        return {s: 1 / top_n for s in top}
    return decide

def ew(cal, stocks):
    me = month_ends(cal)
    def decide(i):
        if cal[i] not in me:
            return None
        el = eligible(stocks, cal[i])
        return {s: 1 / len(el) for s in el} if el else None
    return decide

def hold(sym, start):
    def decide(i):
        return {sym: 1.0} if i == start else None
    return decide

# ---- report ------------------------------------------------------------------------------

def summary(dates, values, start=None):
    """Return over [start, end], each half, max drawdown, yearly returns."""
    if start:
        k = next(j for j, d in enumerate(dates) if d >= start)
        dates, values = dates[k:], values[k:]
    v = values
    h = max(j for j, d in enumerate(dates) if d <= H1_END)
    peak, mdd = v[0], 0.0
    for x in v:
        peak = max(peak, x); mdd = min(mdd, x / peak - 1)
    years = {}
    prev = v[0]
    for j, d in enumerate(dates):
        if j + 1 == len(dates) or dates[j + 1].year != d.year:
            years[d.year] = v[j] / prev - 1; prev = v[j]
    yrs = (dates[-1] - dates[0]).days / 365.25
    return {"start": dates[0], "total": v[-1] / v[0] - 1, "cagr": (v[-1] / v[0]) ** (1 / yrs) - 1,
            "h1": v[h] / v[0] - 1, "h2": v[-1] / v[h] - 1, "mdd": mdd, "years": years}

def row(name, s, trades=None):
    yrs = "  ".join(f"{y} {r:+.0%}" for y, r in s["years"].items())
    t = f"  trades {trades}" if trades is not None else ""
    return (f"{name:26} total {s['total']:+7.1%}  CAGR {s['cagr']:+6.1%}  H1 {s['h1']:+7.1%}  H2 {s['h2']:+7.1%}"
            f"  maxDD {s['mdd']:6.1%}{t}\n{'':26} {yrs}")

def main():
    px, stocks = load_all()
    cal = sorted(px["SPY"])
    tests = [("S1 SPY 200-day trend", {"SPY": px["SPY"]}, s1(cal, px), [("hold SPY", "SPY")]),
             ("S2 sector rotation", {s: px[s] for s in SECTORS}, s2(cal, px), [("hold SPY", "SPY")]),
             ("S3 momentum top 5", stocks, s3(cal, stocks), [("hold SPY", "SPY"), ("equal-weight universe", "EW")])]
    for name, prices, rule, benches in tests:
        d, v, n = simulate(cal, prices, rule)
        s = summary(d, v)
        print(row(name, s, n))
        verdict = True
        for bname, b in benches:
            if b == "EW":
                bd, bv, bn = simulate(cal, stocks, ew(cal, stocks))
            else:
                i0 = cal.index(s["start"]) - 1  # decide the day before the rule's first fill
                bd, bv, bn = simulate(cal, {b: px[b]}, hold(b, i0))
            bs = summary(bd, bv, s["start"])
            print(row(f"  vs {bname}", bs))
            ok = s["h1"] > bs["h1"] and s["h2"] > bs["h2"]
            verdict &= ok
            print(f"{'':26} beats {bname} in both halves: {'YES' if ok else 'NO'}")
        print(f"{'':26} VERDICT: {'PASS' if verdict else 'FAIL'}\n")

if __name__ == "__main__":
    main()
