# Phase 1 results

| Run | Settings (ORATS Custom Backtester, Oct 2020 - Oct 2026) | Trades | Total P/L (1 lot) | Sharpe | Verdict |
|---|---|---|---|---|---|
| R1a SPY put credit spread | 30 DTE, short 0.30 delta, $1 wide, exit +50% / -200%, hold 24d, slippage 75%, $0.65/contract | 203 | **-$1,656** | -1.75 | **FAIL** (negative after costs) |
| R1b SPY put credit spread | same as R1a, exit -100% | 262 | **-$1,846** | -2.33 | **FAIL**: tighter stop is worse |
| R3 SPY iron condor | 30 DTE, shorts 0.16 delta, $1 wings, exit +50% / -200%, hold 23d, slippage 75% | 113 | **-$779** | -0.95 | **FAIL** |
| R3 QQQ iron condor | same | 85 | **-$950** | -1.27 | **FAIL** |
| R4 KO put credit spread | as R1a | 206 | **-$1,220** | -1.63 | **FAIL** |
| R4 XLU put credit spread | as R1a | 211 | **-$1,486** | -2.05 | **FAIL** |
| D1 KO, slippage 0 | as R4 KO, slippage 0 | - | (identical to R4 KO) | - | **INVALID**: file byte-identical to R4_KO.csv |
| D3 KO, no stop, slippage 50 | as D2, slippage 50 | 145 | **-$465** | -0.47 | identical to D2 (slippage 75): slippage field ignored |
| R7 SPY put credit spread, **$5 wide** | as R1a, $5 wide, no stop (min -10) | 143 | **-$51** | 0.03 | FAIL (break-even); each loss ~-$400 = 20% of the account |
| D2 KO, no % stop | as R4 KO, exit min -10 | 145 | **-$465** | -0.47 | FAIL, but the stop was costing ~$755 |

## What the trade logs show (2026-10-15, `analyze_tradelog.py` on results/R1a_SPY.csv, R1b_SPY.csv)

("1000" in ORATS's run title is the 10:00 entry time, not the trade count.)

| | R1a (stop -200%) | R1b (stop -100%) |
|---|---|---|
| Trades | 203 | 262 |
| Win rate | 70% | 56% |
| Avg win / avg loss | +$9.43 / -$50.08 | +$9.52 / -$27.89 |
| Win rate needed to break even | 84% | 75% |
| Avg credit on a $1-wide spread | $0.21 | $0.21 |
| P/L before commissions (fills incl. 75% slippage) | -$1,128 | -$1,165 |
| Commissions | ~$528 | ~$681 |
| Losing years | all 7 (2020-2026) | 6 of 7 |

**Why it fails:** on a $600 stock, $1-wide puts at 0.30 and ~0.29 delta are nearly the same option,
so the spread only collects ~$0.21 (21% of its width) and, after slippage, the trade risks ~$79
to make ~$9. It loses in calm years too, so it isn't a crash problem; it's the structure. With
tiny credits a %-of-credit stop also fires on noise (trade on 2020-11-02 stopped out the same day).
**The fix isn't a tighter or looser stop; it's the underlying:** $1 is only 0.17% of SPY's price.
On a liquid $30-60 ETF, $1 is 2-3% of the price, like a $12-20-wide SPY spread, and still fits the
$60 cap.

Earlier notes on R1a (from the summary screenshot):
- About -$1.66 per trade. Commissions alone are $2.60 per trade (2 legs x $0.65 x open+close),
  about $2,600 over 1000 trades; slippage at 75% of the bid-ask width on 2 legs each way is likely
  several dollars more per trade. On a $1-wide spread the credit is only ~$30, so fixed per-contract
  costs eat it. Not yet proven: diagnostic D1 (same run, slippage 0, commission 0) shows whether the
  rule has any edge before costs.
- The ORATS "Notional Annual Return (Margin)" and the $100,000 equity curve use ORATS's own capital
  assumptions; the per-lot P/L is the number that matters for us.

R1b vs R1a: the tighter stop lost $190 more. Stops on short premium often sell at the worst moment
(after a dip that then recovers); keep the wider stop as the default for later tests.

## Iron condors (R3, 2026-10-15)
| | SPY | QQQ |
|---|---|---|
| Win rate (needed to break even) | 77% (86%) | 73% (88%) |
| Avg win / avg loss | +$10.61 / -$65.48 | +$9.52 / -$66.96 |
| Avg credit (both sides, $1 wings) | $0.26 | $0.27 |
| P/L before commissions | -$192 | -$508 |
| Commissions (4 legs) | $588 | $442 |
| Years | lost 2022-2025 | lost every year but 2020 |

Same structural problem as R1: ~$26 collected against ~$74 at risk, and commissions double with 4 legs.
SPY's condor is nearly break-even before commissions, so on SPY/QQQ the issue is mostly cost.

**Backtester artifact checked:** ORATS applies slippage to each leg separately, so in a fast market a
$1-wide spread's exit was sometimes priced above $1 (impossible with a combo order). It happened on
1-3 trades per run; correcting it changes the totals by $20-130 (R1a -$1,625, R1b -$1,826,
SPY condor -$720, QQQ condor -$820). Every verdict stays FAIL.

## KO and XLU (R4, 2026-10-15)
| | KO | XLU |
|---|---|---|
| Win rate (needed) | 69% (82%) | 66% (82%) |
| Avg win / avg loss | +$8.26 / -$38.11 | +$8.03 / -$36.76 |
| Avg credit on $1 | $0.187 (long leg ~0.21 delta) | $0.181 |
| Before commissions | -$684 | -$937 |
| Stopped out within 1 day of entry | 10 trades, -$257 | 20 trades, -$511 |

- XLU split about 2-for-1 between 2025-11-24 ($87.84) and 2025-12-18 ($43.00); no trade spans it, so
  the results aren't affected.
- Even where $1 is 1-2% of the price, credits after fills are ~$0.18-0.19. The fills (75% of each
  leg's bid-ask, charged on entry and again on exit) cost about as much as the credit.
- **The %-of-credit stop fires on fill noise:** XLU trade 188 (2025-11-24) was stopped out the same
  day while XLU went *up*, because entry+exit slippage alone exceeded the -200% stop on a $0.10
  credit. 9-38 trades per run were stopped within a day. Our live rule is a stop on the *stock
  price*, which this backtester can't model, so these runs test a stop we wouldn't use.

**Next (diagnostics, not pass/fail):** on KO, D2 = no %-stop (MIN -10, the field's floor), exits by
+50% target or the 23-day hold; D1 = same as R4 KO with slippage 0, to see the edge before fill
costs. A rule still has to pass at realistic fills; how realistic 75% is gets checked against real
Webull fills in paper/1-lot trading.

## Diagnostics on KO (2026-10-15)
- **D1 is invalid.** ORATS's title said slip=0%, but its numbers and the downloaded trade log are
  byte-identical to R4 KO (slippage 75). Either the slippage field was ignored or the wrong log was
  downloaded. Until a run with a different slippage changes the result, **we don't know whether
  ORATS applies the slippage field at all**, so the fill cost in every run so far is unverified.
- **D2 (no %-stop):** 145 trades, -$465, win rate 87% (needs 91%), avg win +$7.77 / avg loss -$76.04,
  -$88 before commissions, $377 commissions. 2024 positive, 2022-2023 the worst. Removing the
  stop cut the loss by ~$755: the %-of-credit stop was most of the damage. Without it the rule is
  roughly break-even before commissions, and commissions ($2.60 on an ~$18 credit, 14%) sink it.

## Slippage field (2026-10-15)
D3 (slippage 50) matched D2 (slippage 75) exactly, and D1 (slippage 0) matched R4 KO exactly. The
Custom Backtester isn't applying the slippage field, so **every run so far used ORATS's own,
unknown fill model**, not the "harsh 75%" we set. **ORATS's answer (Otto, 2026-10-15):** the
engine uses its leg-count default, 66% for 2 legs and 53% for condors, i.e. each leg fills 16%
(condors 3%) of its bid-ask width worse than the mid, on entry and exit. So every
run so far was priced at "a bit worse than mid", a moderate, realistic fill for a patient limit
order, not the harsh 75% we intended. The verdicts stand: these rules lose at ordinary fills.

## R7: SPY $5-wide, no stop (2026-10-15)
| | R1a ($1 wide, stop) | R7 ($5 wide, no stop) |
|---|---|---|
| Trades | 203 | 143 |
| Total | -$1,656 | **-$51** |
| Win rate (needed) | 70% (84%) | 88% (88%) |
| Avg win / avg loss | +$9 / -$50 | +$50 / -$373 |
| Avg credit | $0.21 on $1 | $1.00 on $5 |
| Before commissions | -$1,128 | +$320 |
| Years | lost all 7 | 2022 -$988; 2025 -$132; others flat to +$420 |
| Max drawdown (1 lot) | -$1,671 | -$1,922 |

- Width matters: 5x wider took the loss from -$1,656 to break-even. But the rule only made
  +$320 before commissions over 6 years: no edge worth trading.
- Every loss was close to the full width (16 trades at -$405 to -$432), and 2022 alone lost $988.
  At $2,000 one loss is 20% of the account and the drawdown is 96%: not tradable at this size
  even if it were profitable.
- So it isn't only account size: 30-delta, 30-DTE put spreads on SPY were about break-even after
  realistic costs in 2020-2026.

## Phase 1 final round (pre-registered in PHASE1_FINAL.md, amended 2026-10-16)
Each signal row can open its own trade (overlapping); compare each filter with F0 on the same stock.
P/L per 1-lot trade includes ORATS's $0.65/contract commission (leg 1 of trade 1: (5.16-1.99) x 100 - 1.30 = 315.70; log 315.76).

| Run | Trades | Total | Avg/trade | Win % | Avg win / loss | PF | Oct 20-Dec 23 | Jan 24-Oct 26 | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| F1 SPY $5, trend filter | 846 (of 1,078 rows) | +$1,810 | +$2.14 | 89% | +$48 / -$392 | 1.05 | **-$2,853** (PF 0.86) | +$4,663 (PF 1.32) | **FAIL** (bars 2 and 3) |
| F0 KO $1, every day (baseline) | 884 (of 1,495 rows) | -$2,248 | -$2.54 | 88% | +$8 / -$77 | 0.73 | -$2,166 (PF 0.61) | -$82 (PF 0.97) | **FAIL** (baseline) |
| F3 KO $1, trend filter | 529 (of 920 rows) | -$1,004 | -$1.90 | 89% | +$8 / -$77 | 0.78 | -$1,339 (PF 0.59) | +$335 (PF 1.24) | **FAIL** (bars 2, 3, 4: H1 -$4.40/trade vs F0 -$4.13) |
| F4 KO $1, VIX filter | 370 (of 638 rows) | -$607 | -$1.64 | 89% | +$8 / -$79 | 0.81 | -$411 (PF 0.74) | -$196 (PF 0.88) | **FAIL** (bars 2, 3, 4: H2 -$1.04/trade vs F0 -$0.23) |
| F2 SPY $5, VIX filter | 462 (of 638 rows) | +$2,794 | +$6.05 | 89% | +$54 / -$392 | 1.14 | **-$4,059** (PF 0.67) | +$6,852 (PF 1.95) | **FAIL** (bar 2: first half loses; bar 3: PF < 1.2) |

- F2 by year: 2020 +$1,337, 2021 +$1,495, **2022 -$7,327** (120 trades), 2023 +$437 (8), 2024 +$4,587, 2025 +$1,939, 2026 +$327.
  "VIX above its 1-year median" put most entries into the 2022 bear market, where 30-delta puts kept getting run over.
- F1 by year: 2020 +$2,174, 2021 +$3,351, **2022 -$8,461** (65 trades, 58% wins), 2023 +$83, 2024 -$774,
  2025 +$3,240, 2026 +$2,196. Being above the 50-day average didn't keep it out of 2022's losses (bear-market rallies).
  Identified as F1, not F0: all 846 entries are trend-filter days; none fall on the 417 days F1 excludes.
- Scoring: `python3 backtests/score_signals.py LOG [--baseline F0 log]`.
- Up to 17 trades open at once. 176 signal rows opened no trade; 163 of them fell on days when another
  trade was already open (ORATS seems to skip some overlaps; rule **UNVERIFIED**). F0 runs under the same mechanics.
- Exits: 411 profit target, 50 expiration, 1 stop.

**F0 SPY did not finish** (ORATS timed out on the 1,495-row file, 2026-10-16). It can't change any verdict:
F1 and F2 already fail bars 2 and 3 on their own numbers. **All four pre-registered filters fail.**
Per PHASE1_FINAL.md: Phase 1 ends with **"no edge found"** for 30-delta put credit spreads on SPY and KO,
with or without trend/VIX filters, 2020-2026, at ORATS's default fills. What comes next is the owner's decision.

## Owner's trend test: long calls / long puts (pre-registered in PHASE1_TREND_OPTIONS.md)
| Run | Trades | Total (1 lot) | Avg/trade | Win % | Avg win / loss | PF | Oct 20-Dec 23 | Jan 24-Sep 26 |
|---|---|---|---|---|---|---|---|---|
| T2 SPY long put (below 50-day) | 86 (all rows) | **-$20,698** | -$241 | 23% | +$1,239 / -$689 | 0.54 | -$16,481 | -$4,216 |
| T1 SPY long call (above 50-day) | 224 (of 225 rows) | -$696 | -$3 | 40% | +$649 / -$433 | 0.99 | -$5,888 | +$5,191 |
| **T1 + T2 together (the test)** | 310 | **-$21,394** | -$69 | 35% | +$757 / -$517 | 0.79 | -$22,369 | +$975 |

- T2: every exit was the signal (trend flip or 21-day time stop), as planned. One exit (2025-11-26) filled at
  12:26 instead of 10:00, presumably the first quote ORATS had. Only 2025 made money (+$3,120), almost all of it
  from three entries in March 2025 that rode April's crash (+$10,207); without them, -$30,905.
- Downtrends are where puts should shine, yet 2022 lost -$8,634: SPY kept bouncing back above its average
  (trend-flip exits) after the puts had been bought at high prices (implied vol is highest in falls).
- T1 calls by year: 2020 -$921, 2021 -$1,266, **2022 -$9,499** (18 trades, 1 win), 2023 +$5,798, 2024 +$6,438,
  2025 +$2,194, 2026 -$3,440. Calls roughly broke even over six years while SPY itself nearly doubled.
- **Verdict: FAIL** (first half -$22,369; profit factor 0.79). Per the pre-registration, the idea is closed:
  no debit-spread follow-up.


# Stock rules (pre-registered in STOCK_RULES.md, run 2026-10-16; output in results/stock_rules.txt)
Price returns (no dividends) for everything, 0.05% per trade, cash 0%, fills at next open.

| Rule | Total | CAGR | H1 (to Dec 22) | H2 (2023 on) | Max DD | Benchmark (total / H1 / H2 / DD) | Verdict |
|---|---|---|---|---|---|---|---|
| S1 SPY 200-day trend | +97% | 10.2% | +21% | +63% | -23% | SPY +158% / +28% / +102% / -34% | **FAIL** (smaller drawdown, but missed rebounds, e.g. 2020 +7% vs +16%, 2023 +9% vs +24%) |
| S2 sector rotation, top 3 of 11 | +140% | 12.4% | +49% | +61% | -33% | SPY +165% / +31% / +102% / -34% | **FAIL** (won H1, lost H2 badly) |
| S3 momentum, top 5 of ~100 big stocks | +966% | 36.4% | +123% | +378% | -37% | SPY +175% / +36% / +102%; equal-weight list +191% / +55% / +88% | **PASS** as written, but see below |

**S3 is heavily flattered by hindsight (diagnostics, after the verdict; they don't change it):**
- Most-held: NVDA 43 months, AMD 37, PLTR 28, TSLA 25. Without NVDA, PLTR, TSLA and AVGO it is still
  +350% vs the equal-weight list's +159%, and still ahead in both halves.
- But the list is today's giants. It leaves out stocks that had huge runs and then collapsed (2020's
  pandemic winners), which a real momentum rule would have bought. No check on this list can fix that.
- **Unbiased reality check: real momentum funds over the same dates (Mar 2019 - Oct 2026, price only):**
  MTUM +172% vs SPY +175% (tied; behind by 15+ pts in 2021 and 2023); SPMO (S&P 500 momentum) +274%
  (ahead in both halves: H1 +47% vs +36%, H2 +154% vs +102%). For comparison QQQ (Nasdaq 100, not a
  momentum fund) +317%: these years rewarded big tech, which flatters momentum too.
- So real-world momentum here ranged from "same as SPY" to "clearly better", nowhere near +966%.
  Momentum also has long losing stretches (it lagged SPY by 15+ points in 2021 and 2023 in MTUM).

# Trailing stops on hot stocks (pre-registered in STOCK_STOPS.md; output in results/stock_stops.txt)
| | No stop | Stop 15% | Stop 20% | Stop 25% |
|---|---|---|---|---|
| U1 giants (biased against stops): total / maxDD / stop-outs | +966% / -37% | +560% / -43% / 87 | +754% / -43% / 42 | +914% / -37% / 17 |
| U2 + 15 hot 2020 names (biased for stops) | +3,725% / -55% | +1,304% / -60% / 154 | +2,269% / -61% / 89 | +2,877% / -60% / 46 |

**All three levels FAIL on both lists**, and in both halves. Stops didn't even reduce the worst drawdown
(it got worse: they sold near local lows, then the ranking bought back higher).
(The totals themselves are absurd because the lists are hindsight-picked; only the stop vs no-stop
comparison means anything.)

**Why (diagnostic):** the momentum ranking was already the exit. A stock that starts falling loses its
top-5 rank within a month or two, so the rule usually sold the 2020 high-flyers 10-35% off their peaks,
before the real collapse: PTON sold 2021-06-01, then fell another 89% within a year; ZM sold
2021-03-01, then -69%; NVAX sold 2021-07-01 with a +366% gain, then -83%; MRNA sold 2022-02-01, then -33%.
A % stop on top of that mostly added sales on ordinary dips (up to 154 extra stop-outs) in stocks
that then kept rising.
