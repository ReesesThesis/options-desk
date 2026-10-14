"""Multi-leg option positions: net debit/credit, payoff, max loss/profit, breakevens, Greeks, scenarios.

A leg: {"action": "buy"|"sell", "type": "call"|"put", "strike": 140, "expiry": "2026-11-20",
        "price": 2.10, "iv": 0.31 (optional), "qty": 1 (ratio within the structure)}
Dollar figures are per ONE structure (1 contract per ratio unit, x100 shares).
"""
import datetime as dt
from . import bs

MULT = 100

def sign(leg):
    return 1 if leg["action"] == "buy" else -1

def net_premium(legs):
    """Positive = debit paid, negative = credit received, per share."""
    return sum(sign(l) * l.get("qty", 1) * l["price"] for l in legs)

def payoff_at_expiry(legs, S):
    """P/L per structure in $ at expiry, before fees."""
    total = 0.0
    for l in legs:
        intrinsic = max(0.0, S - l["strike"]) if l["type"] == "call" else max(0.0, l["strike"] - S)
        total += sign(l) * l.get("qty", 1) * (intrinsic - l["price"])
    return total * MULT

def _grid(legs):
    ks = sorted({l["strike"] for l in legs})
    pts = [0.0] + ks + [ks[-1] * 3]
    return pts

def max_profit_loss(legs):
    """Returns (max_profit, max_loss) in $; None means unlimited. max_loss is a positive number."""
    pts = _grid(legs)
    vals = [payoff_at_expiry(legs, s) for s in pts]
    # slope beyond the top strike: net calls held
    up_slope = sum(sign(l) * l.get("qty", 1) for l in legs if l["type"] == "call")
    mp = None if up_slope > 0 else max(vals)
    ml = None if up_slope < 0 else -min(vals)
    return mp, (None if ml is None else max(0.0, ml))

def breakevens(legs):
    pts = _grid(legs)
    out = []
    for a, b in zip(pts, pts[1:]):
        fa, fb = payoff_at_expiry(legs, a), payoff_at_expiry(legs, b)
        if fa == 0:
            out.append(a)
        elif fa * fb < 0:
            out.append(a + (b - a) * fa / (fa - fb))
    return sorted(set(round(x, 2) for x in out))

def years_to(expiry, as_of):
    d = dt.date.fromisoformat(expiry) - as_of
    return max(d.days, 0) / 365.0

def leg_iv(leg, spot, as_of, r):
    if leg.get("iv"):
        return leg["iv"]
    T = years_to(leg["expiry"], as_of)
    return bs.implied_vol(leg["type"], leg["price"], spot, leg["strike"], T, r) or 0.30

def position_greeks(legs, spot, as_of, r=0.04):
    """Greeks per structure in $ terms: delta/gamma in share-equivalents, theta $/day, vega $/vol pt."""
    tot = {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}
    for l in legs:
        g = bs.greeks(l["type"], spot, l["strike"], years_to(l["expiry"], as_of), leg_iv(l, spot, as_of, r), r)
        for k in tot:
            tot[k] += sign(l) * l.get("qty", 1) * g[k] * MULT
    return tot

def value(legs, spot, as_of, r=0.04, iv_shift=0.0, days_forward=0):
    """Model P/L per structure in $ if spot/IV/time change (vs entry prices)."""
    when = as_of + dt.timedelta(days=days_forward)
    total = 0.0
    for l in legs:
        iv = max(0.01, leg_iv(l, spot, as_of, r) + iv_shift)
        p = bs.price(l["type"], spot, l["strike"], years_to(l["expiry"], when), iv, r)
        total += sign(l) * l.get("qty", 1) * (p - l["price"])
    return total * MULT

def scenarios(legs, spot, as_of, r=0.04, moves=(-0.05, 0.0, 0.05), iv_shifts=(-0.10, 0.0, 0.10)):
    """P/L grid now and halfway to the nearest expiry. IV shifts are absolute (0.10 = 10 vol points)."""
    entry_ivs = [leg_iv(l, spot, as_of, r) for l in legs]
    fixed = [dict(l, iv=iv) for l, iv in zip(legs, entry_ivs)]
    days = min((dt.date.fromisoformat(l["expiry"]) - as_of).days for l in legs)
    rows = []
    for label, fwd in (("now", 0), (f"in {days // 2}d", days // 2)):
        for ivs in iv_shifts:
            rows.append({"when": label, "iv_shift": ivs,
                         "pnl": [value(fixed, spot * (1 + m), as_of, r, ivs, fwd) for m in moves]})
    return {"moves": list(moves), "rows": rows}
