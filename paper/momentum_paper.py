"""6-month paper test of the top-5 momentum rule (owner, 2026-10-16). No money, no orders.

    python3 paper/momentum_paper.py          # fetch prices from Schwab, advance the log, write the report

Rule (as in backtests/STOCK_RULES.md, S3): rank backtests/universe_large.txt by 12-1 momentum at a
close, "buy" the top 5 equal weight at the next open, hold to the month's last close, "sell" and
re-rank there, filling at the next open. 0.05% cost per side. Benchmarks SPY and SPMO, bought and
sold at the same opens. First ranking: 2026-10-16 close. Last ranking that opens a period:
2027-03-31; the last period closes at the first open after the 2027-04-30 month-end.

Re-running is safe: every fill is the historical open of a fixed date, so a late run gives the
same numbers. State: paper/momentum_state.json; report: paper/MOMENTUM_PAPER.md.
"""
import datetime as dt, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
STATE = os.path.join(ROOT, "paper", "momentum_state.json")
REPORT = os.path.join(ROOT, "paper", "MOMENTUM_PAPER.md")
FIRST = dt.date(2026, 10, 16)
END = dt.date(2027, 4, 30)
COST = 0.0005
TOP = 5
BENCH = ["SPY", "SPMO"]

def universe():
    words = []
    for line in open(os.path.join(ROOT, "backtests", "universe_large.txt")):
        if not line.startswith("#"):
            words += line.split()
    return words

def fetch(symbols, since):
    """{symbol: {date: (open, close)}}; Berkshire is BRK/B at Schwab. Failures are skipped."""
    from desk import schwab
    import time
    out, failed = {}, []
    for s in symbols:
        for attempt in range(3):
            try:
                bars = schwab.daily_bars(s.replace("BRK.B", "BRK/B"), since)
                break
            except Exception as e:
                err = e
                time.sleep(2 * (attempt + 1))
        else:
            failed.append(f"{s} ({err})"); continue
        if bars:  # empty = Schwab has no data for it (BK): permanently outside the universe
            out[s] = {b["date"]: (b["open"], b["close"]) for b in bars}
    if failed:
        # ranking with a stock silently missing would change the picks: stop instead
        sys.exit("Fetch failed after 3 tries, nothing changed: " + "; ".join(failed))
    return out

def complete_days(px, now):
    """SPY trading days whose close is final at `now` (US Eastern wall time)."""
    days = sorted(px["SPY"])
    cutoff = now.date() if now.time() >= dt.time(16, 30) else now.date() - dt.timedelta(days=1)
    return [d for d in days if d <= cutoff]

def month_end_after(cal, d):
    """First completed month-end (last trading day of its month) on or after d, or None."""
    for i in range(len(cal) - 1):
        if cal[i] >= d and cal[i + 1].month != cal[i].month:
            return cal[i]
    return None

def next_day(cal, d):
    return next((x for x in cal if x > d), None)

def rank(px, d, syms):
    mom = {}
    for s in syms:
        if s not in px:
            continue
        closes = [px[s][k][1] for k in sorted(px[s]) if k <= d]
        if len(closes) >= 273:
            mom[s] = closes[-22] / closes[-253] - 1
    top = sorted(mom, key=mom.get, reverse=True)[:TOP]
    return top, {s: round(mom[s], 4) for s in top}

def price_open(px, s, d):
    p = px.get(s, {})
    if d in p:
        return p[d][0]
    prior = [k for k in p if k <= d]
    return p[max(prior)][1] if prior else None  # no trade that day (halt/delisting): last close

def step(state, px, cal, syms):
    """Advance the log as far as the completed data allows. Returns True if anything changed."""
    changed = False
    ps = state["periods"]
    if not ps:
        if FIRST not in cal:
            return False
        top, mom = rank(px, FIRST, syms)
        ps.append({"decided": FIRST.isoformat(), "picks": top, "momentum": mom, "entry": None, "exit": None})
        changed = True
    while True:
        p = ps[-1]
        decided = dt.date.fromisoformat(p["decided"])
        if p["entry"] is None:
            d = next_day(cal, decided)
            if d is None:
                return changed
            p["entry"] = {"date": d.isoformat(), "open": {s: price_open(px, s, d) for s in p["picks"] + BENCH}}
            changed = True
        if p["exit"] is not None:
            return changed
        entry = dt.date.fromisoformat(p["entry"]["date"])
        me = month_end_after(cal, entry)
        if me is None:
            return changed
        d = next_day(cal, me)
        if d is None:
            return changed
        p["exit"] = {"date": d.isoformat(), "month_end": me.isoformat(),
                     "open": {s: price_open(px, s, d) for s in p["picks"] + BENCH}}
        changed = True
        if me >= END:
            state["finished"] = True
            return changed
        top, mom = rank(px, me, syms)
        ps.append({"decided": me.isoformat(), "picks": top, "momentum": mom,
                   "entry": {"date": d.isoformat(), "open": {s: price_open(px, s, d) for s in top + BENCH}},
                   "exit": None})

def ret(p, s, px=None, mark=None):
    a = p["entry"]["open"][s]
    if p["exit"]:
        b = p["exit"]["open"][s]
    else:
        b = px[s][mark][1] if px and s in px and mark in px[s] else None
    if a is None or b is None:
        return None
    return b / a * (1 - COST) ** 2 - 1

def report(state, px=None, mark=None):
    L = ["# Momentum paper test (no money)", "",
         "Top-5 momentum picks from `backtests/universe_large.txt` vs SPY and SPMO, bought and sold at the same opens,",
         "0.05% per side. Rule and dates: `paper/momentum_paper.py`. Started 2026-10-16; ends after the 2027-04-30 month-end.", "",
         "| Period | Picks | Picks | SPY | SPMO |", "|---|---|---|---|---|"]
    cum = {"picks": 1.0, "SPY": 1.0, "SPMO": 1.0}
    for p in state["periods"]:
        if not p["entry"]:
            L.append(f"| ranked {p['decided']}, buy at next open | {', '.join(p['picks'])} | pending | | |")
            continue
        r = [ret(p, s, px, mark) for s in p["picks"]]
        r = [x for x in r if x is not None]
        pr = sum(r) / len(r) if r else None
        spy, spmo = ret(p, "SPY", px, mark), ret(p, "SPMO", px, mark)
        end = p["exit"]["date"] if p["exit"] else f"open (marked {mark})"
        if p["exit"]:
            for k, v in (("picks", pr), ("SPY", spy), ("SPMO", spmo)):
                if v is not None:
                    cum[k] *= 1 + v
        f = lambda x: "n/a" if x is None else f"{x:+.1%}"
        L.append(f"| {p['entry']['date']} to {end} | {', '.join(p['picks'])} | {f(pr)} | {f(spy)} | {f(spmo)} |")
    L += ["", f"**Closed periods, compounded:** picks {cum['picks'] - 1:+.1%}, SPY {cum['SPY'] - 1:+.1%}, "
          f"SPMO {cum['SPMO'] - 1:+.1%}.",
          "", "At the end: the picks must beat **both** SPY and SPMO over the 6 months to be worth real money;",
          "otherwise SPMO stays the satellite. Research, not advice."]
    return "\n".join(L) + "\n"

def main():
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"periods": [], "finished": False}
    if state.get("finished"):
        print("Paper test finished."); print(open(REPORT).read()); return
    syms = universe()
    px = fetch(syms + BENCH, FIRST - dt.timedelta(days=420))
    if "SPY" not in px:
        sys.exit("No SPY data from Schwab: is the sign-in (SCHWAB_REFRESH_TOKEN) expired?")
    from zoneinfo import ZoneInfo
    now = dt.datetime.now(ZoneInfo("America/New_York"))
    cal = complete_days(px, now)
    step(state, px, cal, syms)
    json.dump(state, open(STATE, "w"), indent=1, default=str)
    open(REPORT, "w").write(report(state, px, cal[-1] if cal else None))
    print(open(REPORT).read())

if __name__ == "__main__":
    main()
