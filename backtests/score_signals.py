"""Score an ORATS trade log from a Phase 1 final run against the pre-registered pass bar.

    python3 backtests/score_signals.py TradeLog.csv [more logs, scored as one] [--baseline results/F0_SPY_all.csv]

Finds which signal file the log came from (every entry date must be in it), then prints trades,
total, average, win rate, profit factor, both halves, and P/L by year. Profits in ORATS logs
already include its $0.65/contract commission.
"""
import argparse, collections, csv, datetime as dt, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))
SPLIT = dt.date(2024, 1, 1)

def trades(path):
    by = collections.defaultdict(list)
    for r in csv.DictReader(open(path)):
        by[r["tradeId"]].append(r)
    out = []
    for ls in by.values():
        out.append({"ticker": ls[0]["ticker"], "date": dt.date.fromisoformat(ls[0]["date"]),
                    "exit": dt.date.fromisoformat(ls[0]["exitDate"]), "why": ls[0]["exitReason"],
                    "pnl": sum(float(l["profit"]) for l in ls)})
    return sorted(out, key=lambda t: t["date"])

def source(ts):
    """Signal files that contain every entry date and match the ticker."""
    ent = {t["date"].strftime("%Y%m%d") for t in ts}
    tick = ts[0]["ticker"]
    hits = []
    for p in sorted(glob.glob(os.path.join(HERE, "signals", "[FT]*.csv"))):
        name = os.path.basename(p)[:-4]
        if f"_{tick}_" not in name:
            continue
        rows = {l.split(",")[0][:8] for l in open(p).read().split()[1:]}
        if ent <= rows:
            hits.append((name, len(rows)))
    return hits

def stats(ts):
    if not ts:
        return {"n": 0, "total": 0.0, "avg": 0.0, "win": 0.0, "pf": 0.0, "avg_win": 0.0, "avg_loss": 0.0}
    w = [t["pnl"] for t in ts if t["pnl"] > 0]
    l = [t["pnl"] for t in ts if t["pnl"] <= 0]
    tot = sum(t["pnl"] for t in ts)
    return {"n": len(ts), "total": tot, "avg": tot / len(ts), "win": len(w) / len(ts),
            "pf": sum(w) / -sum(l) if sum(l) else float("inf"),
            "avg_win": sum(w) / len(w) if w else 0.0, "avg_loss": sum(l) / len(l) if l else 0.0}

def line(label, s):
    return (f"{label:18} n={s['n']:4}  total ${s['total']:8,.0f}  avg ${s['avg']:7.2f}  win {s['win']:4.0%}"
            f"  avg win/loss ${s['avg_win']:.0f}/${s['avg_loss']:.0f}  PF {s['pf']:.2f}")

def halves(ts):
    return stats([t for t in ts if t["date"] < SPLIT]), stats([t for t in ts if t["date"] >= SPLIT])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--baseline")
    a = ap.parse_args()
    ts = []
    for log in a.logs:
        part = trades(log)
        hits = source(part)
        # the most specific match is the smallest file that still holds every entry
        print(f"source of {os.path.basename(log)}:",
              ", ".join(f"{n} ({k} rows)" for n, k in sorted(hits, key=lambda h: h[1])) or "UNKNOWN")
        ts += part
    ts.sort(key=lambda t: t["date"])
    s = stats(ts); h1, h2 = halves(ts)
    print(line("all", s)); print(line("Oct 20 - Dec 23", h1)); print(line("Jan 24 - Oct 26", h2))
    for y in sorted({t["date"].year for t in ts}):
        print(line(str(y), stats([t for t in ts if t["date"].year == y])))
    print("exits:", dict(collections.Counter(t["why"] for t in ts)))
    bar = {"1. 60+ trades": s["n"] >= 60,
           "2. profitable in both halves": h1["total"] > 0 and h2["total"] > 0,
           "3. profit factor > 1.2": s["pf"] > 1.2}
    if a.baseline:
        b1, b2 = halves(trades(a.baseline))
        # compare per trade: runs have different trade counts
        bar["4. beats F0 per trade in both halves"] = h1["avg"] > b1["avg"] and h2["avg"] > b2["avg"]
        print(f"baseline avg/trade: H1 ${b1['avg']:.2f}  H2 ${b2['avg']:.2f}")
    for k, v in bar.items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")

if __name__ == "__main__":
    main()
