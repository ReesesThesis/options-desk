"""Trade card: one decided trade, with the exact orders and alerts to set in Webull after the fill."""
import datetime as dt
from . import strategy, risk

def _money(x):
    return "unlimited" if x is None else f"${x:,.0f}"

def _legs_text(legs):
    parts = []
    for l in legs:
        q = l.get("qty", 1)
        parts.append(f"{l['action'].title()} {'' if q == 1 else str(q) + 'x '}{l['expiry']} ${l['strike']:g} {l['type']}")
    return " / ".join(parts)

def build(plan, cfg, open_risk=0.0):
    """Compute everything the card shows. Pure numbers; render() turns it into text."""
    as_of = dt.date.fromisoformat(plan["as_of"]) if plan.get("as_of") else dt.date.today()
    r = cfg["risk_free_rate"]
    legs, spot = plan["legs"], plan["spot"]
    net = strategy.net_premium(legs)
    credit = net < 0
    mp, ml = strategy.max_profit_loss(legs)
    tp_pct = plan.get("take_profit_pct", 50)
    tp_price = abs(net) * (1 - tp_pct / 100) if credit else abs(net) * (1 + tp_pct / 100)
    exp = min(dt.date.fromisoformat(l["expiry"]) for l in legs)
    tdte = plan.get("time_stop_dte", 21)
    return {
        "plan": plan, "as_of": as_of, "credit": credit, "net": abs(net),
        "dte": (exp - as_of).days, "max_profit": mp, "max_loss": ml,
        "breakevens": strategy.breakevens(legs),
        "greeks": strategy.position_greeks(legs, spot, as_of, r),
        "scen": strategy.scenarios(legs, spot, as_of, r),
        "size": risk.size(ml, legs, cfg, open_risk),
        "liquidity": risk.liquidity_problems(legs, cfg),
        "tp_price": tp_price, "tp_pct": tp_pct,
        "time_stop": max(as_of, exp - dt.timedelta(days=tdte)) if tdte else None, "tdte": tdte,
    }

def render(c, cfg):
    p = c["plan"]
    n = c["size"]["contracts"]
    side = "credit" if c["credit"] else "debit"
    limit = p.get("entry_limit")
    L = []
    L.append(f"TRADE CARD: {p['ticker']} {p['structure']}   (as of {c['as_of']}, stock ${p['spot']:.2f})")
    L.append("=" * 72)
    if cfg.get("phase", 0) < 3:
        L.append(f"PAPER TRADE (phase {cfg.get('phase', 0)}): track it, don't put money on it yet.")
    if p.get("thesis"):
        L.append(f"Thesis: {p['thesis']}")
    blockers = []
    if n == 0:
        blockers.append(f"SIZE: {c['size']['reason']}")
    blockers += [f"LIQUIDITY: {x}" for x in c["liquidity"]]
    if blockers:
        L.append("")
        L.append("DO NOT TRADE AS WRITTEN:")
        L += [f"  - {b}" for b in blockers]
    L.append("")
    L.append("ENTER")
    L.append(f"  {_legs_text(p['legs'])}   ({c['dte']} DTE)")
    if limit is not None:
        word = "credit at least" if c["credit"] else "debit at most"
        L.append(f"  One combo order, Limit {side} ${limit:.2f} ({word}). Can't get it? Skip; don't chase.")
    L.append(f"  Model {side} at mid: ${c['net']:.2f}")
    L.append(f"  Size: {n} contract{'s' if n != 1 else ''}"
             + (f"  (worst case ${c['size']['total_risk']:.0f} incl. fees = {c['size']['pct']:.1f}% of ${cfg['account_size']:,})" if n else ""))
    if c["size"].get("reason") and n:
        L.append(f"  Note: {c['size']['reason']}")
    for s in p.get("skip_if", []):
        L.append(f"  Don't enter if: {s}")
    L.append("")
    L.append("NUMBERS (per contract)")
    L.append(f"  Max profit {_money(c['max_profit'])}   Max loss {_money(c['max_loss'])}   "
             f"Breakeven {', '.join(f'${b:.2f}' for b in c['breakevens']) or 'n/a'}")
    g = c["greeks"]
    L.append(f"  Delta {g['delta']:+.1f} sh   Gamma {g['gamma']:+.2f}   Theta ${g['theta']:+.2f}/day   Vega ${g['vega']:+.2f}/vol pt")
    s = c["scen"]
    L.append("  Model P/L by stock move:      " + "".join(f"{m:+.0%}".rjust(9) for m in s["moves"]))
    for row in s["rows"]:
        L.append(f"    {row['when']:>7}, IV {row['iv_shift'] * 100:+3.0f} pts       " + "".join(f"{round(v) + 0:+9d}" for v in row["pnl"]))
    L.append("")
    L.append("RIGHT AFTER YOU'RE FILLED (Webull)")
    close = "Buy-to-close" if c["credit"] else "Sell-to-close"
    L.append(f"  1. ORDER  {close} the whole position as ONE combo order, Limit ${c['tp_price']:.2f}, GTC"
             f"   <- take profit (~{c['tp_pct']}%)")
    L.append("           (Re-figure this from your actual fill: tell Claude 'filled at $X'.)")
    i = 2
    word = {"below": "falls to", "above": "rises to"}
    d = p.get("stop_direction", "below")
    if p.get("warning_level") is not None:
        L.append(f"  {i}. ALERT  {p['ticker']} > Alerts > Price {word[d]} ${p['warning_level']:.2f}   \"{p['ticker']}: warning, re-check thesis\"")
        i += 1
    if p.get("stop_level") is not None:
        L.append(f"  {i}. ALERT  {p['ticker']} > Alerts > Price {word[d]} ${p['stop_level']:.2f}   \"{p['ticker']}: CLOSE IT\"   <- hard stop")
        i += 1
    if c["time_stop"]:
        L.append(f"  {i}. DATE   {c['time_stop']}: close if the target hasn't hit ({c['tdte']} DTE). Phone reminder; the afternoon brief also flags it.")
    L.append("  No stop ORDER on the options themselves: wide option quotes trigger stops on a bad print.")
    if p.get("why"):
        L.append("")
        L.append("WHY THESE LEVELS")
        L += [f"  {w}" for w in p["why"]]
    if p.get("events"):
        L.append("")
        L.append(f"NEWS & EVENTS ({p['ticker']})")
        for e in p["events"]:
            mark = {"warn": "!", "info": "-"}.get(e.get("flag", "info"), "-")
            src = f"  [{e['source']}]" if e.get("source") else ""
            L.append(f"  {mark} {e['text']}{src}")
    if p.get("red_flags"):
        L.append("")
        L.append("RED FLAGS")
        L += [f"  - {x}" for x in p["red_flags"]]
    L.append("")
    L.append("Research, not advice. You place the trade; numbers are model estimates from the quotes above.")
    return "\n".join(L)
