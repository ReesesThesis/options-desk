"""Hard risk rules. These are enforced, not suggested."""
import math

def fees(legs, contracts, cfg, round_trip=True):
    n = sum(l.get("qty", 1) for l in legs) * contracts
    return n * cfg["fee_per_contract_leg"] * (2 if round_trip else 1)

def size(max_loss_per_structure, legs, cfg, open_risk=0.0):
    """Contracts to trade so the worst case (incl. round-trip fees) fits the per-trade and total limits.
    Returns dict with contracts (0 = don't trade) and the reasons."""
    acct = cfg["account_size"]
    if max_loss_per_structure is None:
        return {"contracts": 0, "reason": "undefined (unlimited) loss: defined-risk trades only"}
    budget = acct * cfg["risk_per_trade_pct"] / 100
    cap = acct * cfg["risk_per_trade_hard_cap_pct"] / 100
    room = acct * cfg["max_open_risk_pct"] / 100 - open_risk
    per = max_loss_per_structure + fees(legs, 1, cfg)
    n = math.floor(min(budget, room) / per)
    note = ""
    if n == 0 and per <= min(cap, room):
        n, note = 1, f"1 contract risks ${per:.0f} = {100 * per / acct:.1f}%: above the {cfg['risk_per_trade_pct']}% target, within the {cfg['risk_per_trade_hard_cap_pct']}% hard cap"
    if n == 0:
        return {"contracts": 0, "per_contract_risk": per,
                "reason": f"one contract risks ${per:.0f}; limit is ${min(cap, room):.0f} (hard cap / open-risk room). Use a narrower spread or skip."}
    return {"contracts": n, "per_contract_risk": per, "total_risk": n * per,
            "pct": 100 * n * per / acct, "reason": note}

def liquidity_problems(legs, cfg):
    """Each leg needs bid/ask/oi to be checked; missing data is itself a problem."""
    probs = []
    for l in legs:
        tag = f"{l['type']} {l['strike']:g} {l['expiry']}"
        bid, ask, oi = l.get("bid"), l.get("ask"), l.get("oi")
        if bid is None or ask is None:
            probs.append(f"{tag}: no bid/ask given")
        elif ask > 0:
            mid = (bid + ask) / 2
            pct = 100 * (ask - bid) / mid if mid else 999
            if pct > cfg["max_spread_pct_of_mid"]:
                probs.append(f"{tag}: bid-ask {pct:.0f}% of mid (limit {cfg['max_spread_pct_of_mid']:g}%)")
        if oi is None:
            probs.append(f"{tag}: open interest unknown")
        elif oi < cfg["min_open_interest"]:
            probs.append(f"{tag}: open interest {oi} (min {cfg['min_open_interest']})")
    return probs
