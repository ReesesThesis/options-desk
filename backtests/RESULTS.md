# Phase 1 results

| Run | Settings (ORATS Custom Backtester, Oct 2020 - Oct 2026) | Trades | Total P/L (1 lot) | Sharpe | Verdict |
|---|---|---|---|---|---|
| R1a SPY put credit spread | 30 DTE, short 0.30 delta, $1 wide, exit +50% / -200%, hold 24d, slippage 75%, $0.65/contract | ~1000 | **-$1,656** | -1.75 | **FAIL** (negative after costs) |
| R1b SPY put credit spread | same as R1a, exit -100% | ~1000 | **-$1,846** | -2.33 | **FAIL**: tighter stop is worse |

Notes on R1a (2026-10-15, from the owner's screenshot of the summary):
- About -$1.66 per trade. Commissions alone are $2.60 per trade (2 legs x $0.65 x open+close),
  about $2,600 over 1000 trades; slippage at 75% of the bid-ask width on 2 legs each way is likely
  several dollars more per trade. On a $1-wide spread the credit is only ~$30, so fixed per-contract
  costs eat it. Not yet proven: diagnostic D1 (same run, slippage 0, commission 0) shows whether the
  rule has any edge before costs.
- The ORATS "Notional Annual Return (Margin)" and the $100,000 equity curve use ORATS's own capital
  assumptions; the per-lot P/L is the number that matters for us.

R1b vs R1a: the tighter stop lost $190 more. Stops on short premium often sell at the worst moment
(after a dip that then recovers); keep the wider stop as the default for later tests.
