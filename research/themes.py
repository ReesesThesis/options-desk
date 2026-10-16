"""Theme scan: which industries money is flowing into, from ETF prices alone (no news needed).

    python3 research/themes.py

Columns: 3-month and 6-month return, 12-1 momentum (12 months back to 1 month back, the measure
behind SPMO), and distance from the 52-week high. A MAP for ideas, not a buy signal: the
3-month "hottest sectors" rule lost to SPY in testing (backtests/RESULTS.md, S2).
"""
import sys, datetime as dt, time
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from desk import schwab
T = {"SMH":"Semiconductors","IGV":"Software","CIBR":"Cybersecurity","BOTZ":"Robotics & AI","ARKK":"Disruptive innovation",
     "ITA":"Aerospace & defense","PAVE":"US infrastructure","GRID":"Power grid","NLR":"Nuclear","URA":"Uranium",
     "XLU":"Utilities","ICLN":"Clean energy","TAN":"Solar","LIT":"Lithium & batteries","COPX":"Copper miners",
     "GDX":"Gold miners","SLV":"Silver","XME":"Metals & mining","XOP":"Oil & gas producers","OIH":"Oil services",
     "XHB":"Homebuilders","XRT":"Retail","JETS":"Airlines","KRE":"Regional banks","XBI":"Biotech","IHI":"Medical devices",
     "IBIT":"Bitcoin","IPAY":"Payments/fintech","SPY":"S&P 500 (benchmark)"}
since = dt.date.today() - dt.timedelta(days=430)
rows = []
for s, name in T.items():
    for a in range(3):
        try:
            b = schwab.daily_bars(s, since); break
        except Exception as e:
            time.sleep(2); b = None
    if not b or len(b) < 260:
        print("skip", s, len(b) if b else 0); continue
    c = [x["close"] for x in b]
    r = lambda n: c[-1] / c[-1 - n] - 1
    rows.append((s, name, r(63), r(126), c[-22] / c[-253] - 1, c[-1] / max(c[-252:]) - 1))
spy = [r for r in rows if r[0] == "SPY"][0]
print(f"as of {b[-1]['date']}   SPY: 3m {spy[2]:+.0%}  6m {spy[3]:+.0%}  12-1 {spy[4]:+.0%}")
print(f"{'':5} {'theme':24} {'3m':>6} {'6m':>6} {'12-1':>6} {'off high':>8}")
for s, name, a, b6, m, off in sorted(rows, key=lambda x: -x[4]):
    print(f"{s:5} {name:24} {a:+6.0%} {b6:+6.0%} {m:+6.0%} {off:+8.0%}")
