# Owner's test: buy calls in an uptrend, puts in a downtrend (pre-registered 2026-10-16)

Asked for by the owner after the Phase 1 final round failed ("for my peace of mind").
Written down **before** any run, so nothing can be tuned after seeing results. One shot: if it
fails, it's recorded and we don't try variations of it.

## The rule (SPY only)
- **When:** every week, on its first trading day D, at 10:00.
- **Trend:** SPY's close on D-1 vs its 50-day simple average (the 50 closes ending D-1), the same
  trend definition as F1.
- **Above:** buy one call (run T1). **Below:** buy one put (run T2). Never both.
- **Option:** about 30 days to expiration (target 30, min 25, max 30), at the money (delta
  target 0.50, min 0.45, max 0.55; for puts ORATS's delta field is entered the same way as before).
- **Exit**, whichever comes first:
  1. the trend flips: 10:00 on the first day whose prior close is on the other side of the average;
  2. time stop: 16:00 on the last trading day within 21 calendar days of entry (about 9 days
     before expiration, before time decay speeds up).
  No profit-target or %-stop exits. Weekly entries can overlap (up to 3 open in a long trend).
- Files: `signals/T1_SPY_call.csv` (225 entries), `signals/T2_SPY_put.csv` (86), from
  `make_trend_options.py`. Entries Oct 2020 to Sep 15 2026.

## ORATS settings (both runs)
Strategy Long Call (T1) / Long Put (T2) (exact names in ORATS's list: **UNVERIFIED**), DTE 30/25/30,
delta 0.5/0.45/0.55, Exit Profit/Loss % left empty (if required: MIN -10, MAX 10, i.e. off),
Max Hold 23 (the signal exit always comes first), commission 0.65, date range All.
ORATS fills 1-leg trades at 75% of the bid-ask (FACTS.md); SPY at-the-money quotes are a few cents
wide, so that costs little.

## Pass bar (calls and puts scored together as one strategy; each side also reported)
1. 60+ trades.
2. Profitable after costs in **both** halves: Oct 2020 - Dec 2023 and Jan 2024 - Sep 2026.
3. Profit factor above 1.2.

## Account fit (decided now, whatever the result)
An at-the-money 30-day SPY option costs roughly $1,500-2,000 (SPY ~$770), 25-30x the desk's
$60 per-trade cap. So even a pass is "valid but not tradable at $2,000 as single options"; it
would justify designing a defined-risk version (a debit spread sized to the cap) and testing
that separately. A fail ends the idea.
