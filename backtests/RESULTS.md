# Phase 1 results

| Run | Settings (ORATS Custom Backtester, Oct 2020 - Oct 2026) | Trades | Total P/L (1 lot) | Sharpe | Verdict |
|---|---|---|---|---|---|
| R1a SPY put credit spread | 30 DTE, short 0.30 delta, $1 wide, exit +50% / -200%, hold 24d, slippage 75%, $0.65/contract | 203 | **-$1,656** | -1.75 | **FAIL** (negative after costs) |
| R1b SPY put credit spread | same as R1a, exit -100% | 262 | **-$1,846** | -2.33 | **FAIL**: tighter stop is worse |
| R3 SPY iron condor | 30 DTE, shorts 0.16 delta, $1 wings, exit +50% / -200%, hold 23d, slippage 75% | 113 | **-$779** | -0.95 | **FAIL** |
| R3 QQQ iron condor | same | 85 | **-$950** | -1.27 | **FAIL** |

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
