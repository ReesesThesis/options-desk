# options-desk: instructions for agents

This repo is the owner's options research desk. **Agents research; the owner places every trade
himself, in Webull.** Nothing in this repo sends orders, and no agent ever does. The owner traded
small sums before and is now trading seriously with a **$2,000 account** (`config.json`).
Bring him **one decided trade or "no trade"**, never a menu of options.

## Ground rules (from the research, 2026-10-14)

- Retail options *buyers* lose on average (Bryzgalova et al. 2023, JF; de Silva/Smith/So, RoF 2025:
  5-14% losses buying options around earnings). Don't recommend buying calls or puts into earnings.
- Implied vol is usually above realized vol, so **defined-risk premium selling** (credit spreads,
  iron condors) is the default edge. Debit trades need a stated reason why IV is cheap.
- Options flow (Unusual Whales etc.) is weak evidence on its own: public prints don't show opening vs
  closing or hedges. Use it as context, never as the only reason for a trade.
- Headlines are context, not signals: they're priced in within seconds.
- **Defined risk only.** No naked short options, ever. No 0DTE.
- Every number on a card comes from code on real quotes (`desk/`), never from memory. Missing data
  is written "MISSING", and the trade waits.

## Getting facts right (owner, 2026-10-15, after a $49 promo price was passed off as the list price)

- Any outside fact that costs money, sets a limit, or affects a trade (prices, plan limits, broker
  rules, API details, earnings dates) goes in `FACTS.md` with its source and status. Look there first.
- Say how you know: "verified on <official page> today", or say plainly "UNVERIFIED" in bold.
  Search summaries, third-party sites and memory are UNVERIFIED. Discounts and promos are not prices.
- If the official page won't load from the cloud, say so and ask the owner to read it; don't fill
  the gap with a secondhand number.
- Before the owner spends money or enters a trade, list every UNVERIFIED fact it depends on.
- Trade cards: the owner checks Webull's own max profit / max loss / breakeven on the order screen
  against the card before submitting. If they differ by more than $2, don't send it; tell Claude.
- Market data: a quote older than 20 minutes, or Schwab and ORATS disagreeing on a mid by more than
  10%, is printed on the card as a warning, and the trade waits.

## Risk rules (enforced in `desk/risk.py`; change only on the owner's word)

- Size on the full worst case incl. round-trip fees: 2% target ($40), **3% hard cap ($60)** per trade.
  At $2,000 that means **$1-wide spreads** on liquid names; wider ones get "DO NOT TRADE AS WRITTEN".
- Total open risk <= 10% ($200), at most 4 positions.
- Stop trading for the week after -6%, for the month after -10%.
- Liquidity per leg: bid-ask <= 10% of mid, open interest >= 500.
- Exits: take profit ~50% of max (credit) as a GTC combo order; hard stop = an alert on the
  **stock price** where the thesis is wrong; time stop at 21 DTE. No stop orders on option legs.
- Webull margin is required for spreads, and Webull needs $2,000+ equity for margin: if the account
  dips below that, spreads stop being possible. Say so in the brief if it's within $100.

## Phases (each has a gate; don't skip)

0. Tools (this repo): data, Greeks/IV, filings, trade cards, journal. Gate: numbers match Webull/Schwab.
1. Backtests (ORATS history): 3-5 candidate rules incl. one "follow the flow" rule as an honest test.
   Gate: positive expectancy after costs on 100+ trades, across different years. If none pass, say so.
2. Paper trading the survivors for 2-3 months with live briefs. Gate: live close to backtest.
3. Real money, starting at 1 contract per card, for 50 trades before anything grows.
Current phase: **0**. Until phase 3, every card is marked PAPER at the top.

## Scheduled runs

- **Pre-market (8:45 ET, weekdays):** `python3 desk.py status`; check open positions vs levels and
  events; scan the watchlist (`context`, `filings`, news); write at most 1-2 cards (or "no trade
  today" with the reason) to `briefs/<date>.md`, commit, push to main, and send the owner a push
  notification with the short version.
- **After close (4:30 ET):** each open trade: distance to stop/warning, P/L, time stop due, new
  filings or event dates inside the trade. Anything to do gets one line with the exact order.
- **Weekend:** journal stats vs backtest, what worked, what to change. Warn if the Schwab sign-in
  has <= 1 day left (`SCHWAB_REFRESH_ISSUED`).

## Trade cards

Write a plan JSON in `plans/` (format: `plans/EXAMPLE_xyz_bull_put.json`), then
`python3 desk.py card plans/<file>.json --save`. The card holds the entry limit, size, numbers,
Greeks and scenarios, and the **exact Webull orders and alerts to set right after the fill**,
plus why each level, news and events with dates and links, and red flags.
When the owner says "filled at $X", run `python3 desk.py fill plans/<file>.json X N`, re-figure the
take-profit from his fill, and tell him if any level changed. Closes: `desk.py close ID PRICE`.

## News, filings and events

Before every card: earnings date, ex-dividend, shareholder meeting/proxy votes (DEF 14A), 8-Ks,
Form 4 insider trades (open-market buys by several insiders matter; 10b5-1 sales mostly don't),
13D/13G stakes, offerings (S-3/424B), and macro dates (FOMC, CPI, jobs). An event inside the trade
either is the point of the trade or moves the expiration/skips it. Every item gets a date and a
source link. Rumors are labeled and never change a trade alone. Public information only.

## Setup (cloud environment settings)

Allowed domains: `api.schwabapi.com`, `www.sec.gov`, `data.sec.gov`, `efts.sec.gov`, plus
`api.orats.io` and the news provider when added. Environment variables: `SCHWAB_APP_KEY`,
`SCHWAB_APP_SECRET`, `SCHWAB_REFRESH_TOKEN`, `SCHWAB_REFRESH_ISSUED` (YYYY-MM-DD), `SEC_USER_AGENT`
("options-desk <email>"), later `ORATS_TOKEN`. Never print, save or ask for a key in chat.
Schwab refresh tokens last 7 days: the owner renews with `python3 -m desk.schwab_login` on his PC.

## Commands

```
python3 desk.py status                       # open trades, open risk, results, Schwab days left
python3 desk.py context TICKER               # spot, RV20/30, ATM IV, expected move per expiry
python3 desk.py filings TICKER --days 30     # SEC filings that matter
python3 desk.py card plans/X.json --save     # trade card -> briefs/
python3 desk.py fill plans/X.json PRICE N    # journal a fill
python3 desk.py close ID PRICE --fees F      # journal a close
python3 -m unittest discover -s tests        # tests (stdlib only, no installs)
```

Every card and brief ends with: "Research, not advice. You place the trade."
