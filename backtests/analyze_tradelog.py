"""Summarize a 2-leg ORATS trade log: python3 backtests/analyze_tradelog.py backtests/results/R1a_SPY.csv ..."""
import csv, sys, collections
for f, name in [(p, p) for p in sys.argv[1:]]:
    rows=list(csv.DictReader(open(f)))
    T=collections.OrderedDict()
    for r in rows:
        t=T.setdefault(r["tradeId"],{"legs":[]}); t["legs"].append(r)
    out=[]
    for tid,t in T.items():
        L=t["legs"]; p=sum(float(x["profit"]) for x in L)
        sh=[x for x in L if x["ratio"].startswith("-")][0]; lg=[x for x in L if not x["ratio"].startswith("-")][0]
        credit=float(sh["tradeOptPx"])-float(lg["tradeOptPx"])
        exitc=float(sh["exitOptionPx"])-float(lg["exitOptionPx"])
        width=float(sh["strike"])-float(lg["strike"])
        out.append(dict(date=sh["date"],exit=sh["exitDate"],p=p,credit=credit,exitc=exitc,width=width,reason=sh["exitReason"],year=sh["date"][:4],gross=(credit-exitc)*100))
    n=len(out); P=[o["p"] for o in out]; W=[x for x in P if x>0]; Ls=[x for x in P if x<=0]
    print(f"\n=== {name}: {n} trades, total ${sum(P):.0f}, avg ${sum(P)/n:.2f}/trade")
    print(f"win rate {len(W)/n:.0%}, avg win ${sum(W)/len(W):.2f}, avg loss ${sum(Ls)/len(Ls):.2f}, worst ${min(P):.2f}")
    print(f"avg credit ${sum(o['credit'] for o in out)/n:.3f} on avg width ${sum(o['width'] for o in out)/n:.2f}")
    g=sum(o['gross'] for o in out); print(f"gross (price change only, fills as logged) ${g:.0f}; commissions ~${n*2.6:.0f}; total ${sum(P):.0f}")
    print("exit reasons", collections.Counter(o["reason"] for o in out))
    by=collections.defaultdict(list)
    for o in out: by[o["year"]].append(o["p"])
    for y in sorted(by): print(f"  {y}: {len(by[y]):3d} trades  ${sum(by[y]):8.0f}  win {sum(1 for x in by[y] if x>0)/len(by[y]):.0%}")
    # running drawdown 1 lot sequential (ignoring overlap)
    eq=0;pk=0;dd=0;streak=0;ms=0
    for x in P:
        eq+=x;pk=max(pk,eq);dd=min(dd,eq-pk)
        streak=streak+1 if x<=0 else 0; ms=max(ms,streak)
    print(f"max drawdown ${dd:.0f}, longest losing streak {ms}")
