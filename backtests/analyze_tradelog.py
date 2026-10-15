"""Summarize ORATS Custom Backtester trade logs (any number of legs).

    python3 backtests/analyze_tradelog.py backtests/results/R1a_SPY.csv [more.csv ...]

Per trade: net credit (+) or debit (-) at entry from the logged fills (slippage included),
P/L after commissions (ORATS's `profit` column), and yearly / exit-reason breakdowns.
"""
import collections, csv, sys

COMMISSION = 0.65

def trades(path):
    T = collections.OrderedDict()
    for r in csv.DictReader(open(path)):
        T.setdefault(r["tradeId"], []).append(r)
    out = []
    for legs in T.values():
        q = lambda r: float(r["ratio"])
        net = sum(-q(r) * float(r["tradeOptPx"]) for r in legs)          # + = credit
        p = sum(float(r["profit"]) for r in legs)
        n_contracts = sum(abs(q(r)) for r in legs)
        out.append({"date": legs[0]["date"], "year": legs[0]["date"][:4], "p": p, "net": net,
                    "fees": n_contracts * COMMISSION * 2, "reason": legs[0]["exitReason"],
                    "legs": len(legs)})
    return out

def report(path):
    out = trades(path)
    n = len(out); P = [o["p"] for o in out]
    W = [x for x in P if x > 0]; L = [x for x in P if x <= 0]
    aw = sum(W) / len(W) if W else 0; al = sum(L) / len(L) if L else 0
    fees = sum(o["fees"] for o in out)
    print(f"\n=== {path}: {n} trades ({out[0]['legs']} legs), total ${sum(P):.0f}, avg ${sum(P) / n:.2f}/trade")
    print(f"win rate {len(W) / n:.0%} (break-even needs {(-al) / (aw - al):.0%}), avg win ${aw:.2f}, avg loss ${al:.2f}, worst ${min(P):.2f}")
    print(f"avg entry {'credit' if out[0]['net'] > 0 else 'net'} ${sum(o['net'] for o in out) / n:.3f}/share; "
          f"before commissions ${sum(P) + fees:.0f}, commissions ${fees:.0f}")
    print("exits:", dict(collections.Counter(o["reason"] for o in out)))
    by = collections.defaultdict(list)
    for o in out:
        by[o["year"]].append(o["p"])
    print("  " + "  ".join(f"{y}: ${sum(v):.0f} ({len(v)})" for y, v in sorted(by.items())))
    eq = pk = dd = 0; streak = ms = 0
    for x in P:
        eq += x; pk = max(pk, eq); dd = min(dd, eq - pk)
        streak = streak + 1 if x <= 0 else 0; ms = max(ms, streak)
    print(f"max drawdown ${dd:.0f} (1 lot, trades in sequence), longest losing streak {ms}")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        report(p)
