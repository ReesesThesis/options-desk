#!/usr/bin/env python3
"""options-desk command line. Research only: nothing here places orders.

  python3 desk.py card plans/X.json [--save]     trade card from a plan (sized to config.json)
  python3 desk.py context TICKER                 spot, realized vol, ATM IV and expected move by expiry (Schwab)
  python3 desk.py filings TICKER [--days 30]     recent SEC filings that matter (EDGAR)
  python3 desk.py fill plans/X.json PRICE N      log a fill in the journal (PRICE = net per share)
  python3 desk.py close ID PRICE [--fees F]      log a close
  python3 desk.py status                         open trades, open risk, results, Schwab sign-in days left
"""
import argparse, datetime as dt, json, os, sys
from desk import card, config, journal, vol

def cmd_card(a, cfg):
    plan = json.load(open(a.plan))
    c = card.build(plan, cfg, journal.open_risk())
    text = card.render(c, cfg)
    print(text)
    if a.save:
        out = os.path.join(config.ROOT, "briefs", f"{c['as_of']}_{plan['ticker']}.txt")
        open(out, "w").write(text + "\n")
        print(f"\nsaved {out}")

def cmd_context(a, cfg):
    from desk import schwab
    t = a.ticker.upper()
    closes = [c for _, c in schwab.daily_closes(t)]
    ch = schwab.chain(t, dt.date.today(), dt.date.today() + dt.timedelta(days=60), strike_count=6)
    spot = ch["spot"]
    print(f"{t}  spot ${spot:.2f}   RV20 {vol.realized_vol(closes, 20):.1%}   RV30 {vol.realized_vol(closes, 30):.1%}")
    by_exp = {}
    for k in ch["contracts"]:
        by_exp.setdefault(k["expiry"], []).append(k)
    for exp in sorted(by_exp):
        ks = by_exp[exp]
        atm = min({k["strike"] for k in ks}, key=lambda s: abs(s - spot))
        c = next((k for k in ks if k["type"] == "call" and k["strike"] == atm), None)
        p = next((k for k in ks if k["type"] == "put" and k["strike"] == atm), None)
        if not (c and p and c["mark"] and p["mark"]):
            continue
        em = vol.expected_move_from_straddle(c["mark"], p["mark"])
        days = (dt.date.fromisoformat(exp) - dt.date.today()).days
        ivs = [x["iv"] for x in (c, p) if x["iv"]]
        iv = sum(ivs) / len(ivs) if ivs else 0.0
        print(f"  {exp} ({days:>2}d)  ATM {atm:g}  IV {iv:.1%}  straddle ${em['straddle']:.2f}"
              f"  ~1sd move ${em['one_sd']:.2f} ({em['one_sd'] / spot:.1%})")
    left = schwab.refresh_days_left()
    if left is not None and left <= 1:
        print(f"\n!! Schwab sign-in expires in {left} day(s): run desk.schwab_login and update the settings.")

def cmd_filings(a, cfg):
    from desk import sec
    rows = sec.recent_filings(a.ticker, a.days)
    if not rows:
        print(f"No watched filings for {a.ticker.upper()} in {a.days} days.")
    for f in rows:
        print(f"  {f['date']}  {sec.describe(f):<45} {f['url']}")

def cmd_fill(a, cfg):
    plan = json.load(open(a.plan))
    c = card.build(plan, cfg, journal.open_risk())
    r = journal.open_trade(c, a.price, a.contracts)
    print(f"logged {r['id']}: {r['contracts']} x {r['structure']} at ${r['fill']} ({r['side']}); "
          f"take profit ${r['take_profit']}, worst case ${r['max_loss_total']}")

def cmd_close(a, cfg):
    r = journal.close_trade(a.id, a.price, a.fees)
    print(f"closed {r['id']} at ${r['exit']}: P/L ${r['pnl']}")

def cmd_status(a, cfg):
    acct = cfg["account_size"]
    rows = journal.open_trades()
    risk = journal.open_risk()
    print(f"Account ${acct:,}  open risk ${risk:.0f} ({100 * risk / acct:.1f}% of {cfg['max_open_risk_pct']:g}% max)"
          f"  open positions {len(rows)}/{cfg['max_open_positions']}")
    today = dt.date.today()
    for r in rows:
        flag = "  <- TIME STOP" if r["time_stop"] and dt.date.fromisoformat(r["time_stop"]) <= today else ""
        print(f"  {r['id']}: {r['contracts']} x {r['ticker']} {r['structure']} @ ${r['fill']}  TP ${r['take_profit']}"
              f"  stop {r['stop_direction']} ${r['stop_level']}  time stop {r['time_stop']}{flag}")
    s = journal.stats()
    if s["trades"]:
        print(f"Closed: {s['trades']} trades, win rate {s['win_rate']:.0%}, total ${s['total']:.0f}, "
              f"avg win ${s['avg_win']:.0f}, avg loss ${s['avg_loss']:.0f}, expectancy ${s['expectancy']:.2f}/trade")
    from desk import schwab
    left = schwab.refresh_days_left()
    if left is not None:
        print(f"Schwab sign-in: {left} day(s) left" + ("  <- RENEW NOW" if left <= 1 else ""))

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("card"); p.add_argument("plan"); p.add_argument("--save", action="store_true")
    p = sub.add_parser("context"); p.add_argument("ticker")
    p = sub.add_parser("filings"); p.add_argument("ticker"); p.add_argument("--days", type=int, default=30)
    p = sub.add_parser("fill"); p.add_argument("plan"); p.add_argument("price", type=float); p.add_argument("contracts", type=int)
    p = sub.add_parser("close"); p.add_argument("id"); p.add_argument("price", type=float); p.add_argument("--fees", type=float, default=0.0)
    sub.add_parser("status")
    a = ap.parse_args(argv)
    globals()[f"cmd_{a.cmd}"](a, config.load())

if __name__ == "__main__":
    main()
