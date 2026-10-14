"""Trade journal: journal/trades.csv. Every card that gets filled is logged, and every close."""
import csv, datetime as dt, json, os
from .config import ROOT

PATH = os.path.join(ROOT, "journal", "trades.csv")
FIELDS = ["id", "opened", "ticker", "structure", "legs", "contracts", "side", "fill",
          "take_profit", "warning_level", "stop_level", "stop_direction", "time_stop",
          "max_loss_total", "status", "closed", "exit", "pnl", "notes"]

def _read():
    if not os.path.exists(PATH):
        return []
    with open(PATH, newline="") as f:
        return list(csv.DictReader(f))

def _write(rows):
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    with open(PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

def open_trade(card, fill, contracts, notes=""):
    """card: output of card.build(); fill: actual net price per share (positive)."""
    rows = _read()
    p = card["plan"]
    # A better fill than the model price lowers the worst case (more credit, or a smaller debit).
    width_loss = card["max_loss"] - (fill - card["net"]) * 100 * (1 if card["credit"] else -1)
    tp = fill * (1 - card["tp_pct"] / 100) if card["credit"] else fill * (1 + card["tp_pct"] / 100)
    tid = f"{dt.date.today():%Y%m%d}-{p['ticker']}-{len(rows) + 1}"
    rows.append({"id": tid, "opened": str(dt.date.today()), "ticker": p["ticker"],
                 "structure": p["structure"], "legs": json.dumps(p["legs"]), "contracts": contracts,
                 "side": "credit" if card["credit"] else "debit", "fill": f"{fill:.2f}",
                 "take_profit": f"{tp:.2f}", "warning_level": p.get("warning_level", ""),
                 "stop_level": p.get("stop_level", ""), "stop_direction": p.get("stop_direction", "below"),
                 "time_stop": str(card["time_stop"] or ""), "max_loss_total": f"{width_loss * contracts:.0f}",
                 "status": "open", "closed": "", "exit": "", "pnl": "", "notes": notes})
    _write(rows)
    return rows[-1]

def close_trade(tid, exit_price, fee_total=0.0, notes=""):
    rows = _read()
    for r in rows:
        if r["id"] == tid and r["status"] == "open":
            n, fill = int(r["contracts"]), float(r["fill"])
            per = (fill - exit_price) if r["side"] == "credit" else (exit_price - fill)
            r.update(status="closed", closed=str(dt.date.today()), exit=f"{exit_price:.2f}",
                     pnl=f"{per * 100 * n - fee_total:.2f}", notes=(r["notes"] + " " + notes).strip())
            _write(rows)
            return r
    raise KeyError(f"no open trade {tid}")

def open_trades():
    return [r for r in _read() if r["status"] == "open"]

def open_risk():
    return sum(float(r["max_loss_total"] or 0) for r in open_trades())

def stats():
    closed = [r for r in _read() if r["status"] == "closed"]
    if not closed:
        return {"trades": 0}
    pnl = [float(r["pnl"]) for r in closed]
    wins = [x for x in pnl if x > 0]
    losses = [x for x in pnl if x <= 0]
    return {"trades": len(pnl), "win_rate": len(wins) / len(pnl), "total": sum(pnl),
            "avg_win": sum(wins) / len(wins) if wins else 0.0,
            "avg_loss": sum(losses) / len(losses) if losses else 0.0,
            "expectancy": sum(pnl) / len(pnl)}
