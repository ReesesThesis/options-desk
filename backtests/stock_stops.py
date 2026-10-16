"""Trailing stops on the momentum picks (pre-registered in STOCK_STOPS.md).

    python3 backtests/stock_stops.py
"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stock_rules as sr

def s3_stop(cal, stocks, stop, top_n=5):
    """S3 momentum; between month-ends, sell a holding at the next open once its close is `stop`
    below its highest close since the month-end decision. Bought back only by the next ranking."""
    base = sr.s3(cal, stocks, top_n)
    st = {"highs": {}, "log": []}
    def decide(i):
        d = cal[i]
        t = base(i)
        if t is not None:
            st["highs"] = {s: stocks[s][d][1] for s in t}
            return t
        out = []
        for s, hi in list(st["highs"].items()):
            if d not in stocks[s]:
                continue
            c = stocks[s][d][1]
            st["highs"][s] = hi = max(hi, c)
            if c <= hi * (1 - stop):
                out.append(s)
                st["log"].append((d, s, c))
                del st["highs"][s]
        return {"_sell": out} if out else None
    return decide, st

def run(cal, stocks, label):
    d, v, n = sr.simulate(cal, stocks, sr.s3(cal, stocks))
    base = sr.summary(d, v)
    print(sr.row(f"{label}: no stop", base, n))
    verdicts = {}
    for stop in (0.15, 0.20, 0.25):
        rule, st = s3_stop(cal, stocks, stop)
        d2, v2, n2 = sr.simulate(cal, stocks, rule)
        s = sr.summary(d2, v2)
        print(sr.row(f"{label}: stop {stop:.0%}", s, n2))
        # stopped stocks that were bought back later at a higher price than where they were sold
        log = st["log"]
        print(f"{'':26} stop-outs {len(log)}")
        verdicts[stop] = s["h1"] > base["h1"] and s["h2"] > base["h2"]
        print(f"{'':26} beats no-stop in both halves: {'YES' if verdicts[stop] else 'NO'}")
    return verdicts, base

def main():
    px, u1 = sr.load_all()
    cal = sorted(px["SPY"])
    hot = {os.path.basename(p)[:-4]: sr.load(p) for p in glob.glob(os.path.join(sr.HERE, "data", "stocks_hot", "*.csv"))}
    u2 = {**u1, **hot}
    v1, _ = run(cal, u1, "U1 giants")
    print()
    v2, _ = run(cal, u2, "U2 +hot2020")
    print()
    for stop in (0.15, 0.20, 0.25):
        print(f"stop {stop:.0%}: {'PASS' if v1[stop] and v2[stop] else 'FAIL'} (U1 {'yes' if v1[stop] else 'no'}, U2 {'yes' if v2[stop] else 'no'})")

if __name__ == "__main__":
    main()
