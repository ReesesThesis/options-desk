# Phase 1 backtests in ORATS Trading Tools (owner runs them; Claude grades them)

ORATS's backtester screen hasn't been seen yet, so the setting names below are descriptive, not
ORATS's labels. **Step 0 first**, then the runs.

## Step 0: check the settings screen (send a screenshot)
Confirm the backtester lets you set: date range back to 2007, commission per contract, slippage /
fill price (mid vs. bid-ask), earnings avoidance, IV rank filter, profit target %, stop loss %,
exit at N days to expiration, and an export of the full trade list (CSV). Anything missing changes
the rules below, so stop and tell Claude before running.

## What Step 0 found (2026-10-15)
The Custom Backtester's data starts in **2020**. That still covers the 2020 crash, the 2022 bear
market and the April 2025 sell-off, but not 2008, so the pass bar below requires each rule to be
looked at in 2020 and 2022 on their own. It has no IV-rank or earnings filter on screen; R2 and R4's
filters will come from a signal CSV (entry dates) that Claude builds, once a data source for IV
history and earnings dates is connected. Run R1, R3 and R5 first.

### R1 on the Custom Backtester screen
- Symbol **SPY** (not SPX: SPX strikes are $5 apart and 10x the size), strategy Put Credit Spread.
- Date: **All** through the latest date. Time: **10:00am** entry. Expiry: Both.
- Days to Expiration: target **30**, min **25**, max **30** (this backtester caps leg 1 at 30 DTE). DTE diff 0.
- Strike Selection, leg 1 (short put): delta target 0.30, min 0.25, max 0.35.
  Leg 2 (long put): pts OTM **1** from Ref Leg 1 (a $1-wide spread). Ratio -1 / 1.
- Days to Expiration, DTE DIFF for leg 2: **0 / 0 / 0** (same expiration as leg 1; anything else
  makes it a diagonal).
- Exit Profit/Loss % takes decimals: max **0.5**, min **-2** (R1a) and a second run with min **-1** (R1b).
  On a $1-wide spread a -2 stop may sit beyond the max loss and never fire; R1b shows the effect of
  a tighter stop.
- Trade % Slippage: **75** (worse than the 66 default for 2 legs, on purpose). Commission 0.65.
- Max Hold Days: **23** (exit with about 7 days left, before the last week's gamma risk).
  If a 30-DTE rule passes, the live time stop becomes 7 DTE to match what was tested.
- Wide Bid Ask Filter: leave 5 / 15.
R3: same, strategy Iron Condor, both short legs delta ~0.16 (0.12-0.20), wings 1 pt.
R5: strategy Long Call, delta 0.50 (0.45-0.55), Exit P/L max 0.5 min -0.5, slippage 75, Max Hold Days 23.

### Next runs (2026-10-15, after R1a/R1b)
R1 failed because $1 is too narrow on a $600 stock (see RESULTS.md). Single stocks and cheaper ETFs,
where $1 is 1-3% of the price, are the next test. Same settings as R1a (30/25/30 DTE, short put
0.30 delta, long put 1 pt lower, exit +0.5 / -2, slippage 75, commission 0.65, hold 23), symbol only:
- **R4 (stocks the owner wants to trade):** KO, XLU (utilities ETF), plus 2-3 more he picks
  (e.g. PEP, DUK, SO, JPM). First check each in ORATS: price roughly $30-120 and strikes $1 apart.
  No earnings filter on this screen, so this is the unfiltered baseline; earnings inside a trade can
  hurt it. The filtered version (signal CSV of entry dates that skip earnings) comes once SEC access
  gives us earnings dates.
- **R6 (cheaper ETFs):** XLF, EEM (or SLV / GDX), if their prices fit.
- **R5:** long call control on SPY. R3 (condors on SPY/QQQ/IWM) is dropped: same width problem, 4 legs.

## Same settings for every run
- Dates: earliest available (2007 if offered) through the latest date.
- Commission: **$0.60 per contract per leg**, each way (the Webull fee estimate in config.json).
- Fills: the **worst** realistic option offered (e.g. 50-75% of the way from mid to the bid/ask).
  If it offers both "mid" and something worse, run the worse one.
- Entries: every week (or the closest setting), so there are 100+ trades.
- Export: the **full trade list as CSV** plus the summary screen. Upload both to GitHub:
  options-desk > `backtests/results/` > Add file > Upload files, named like `R1_SPY.csv`.

## The rules
| # | Rule | Tickers | Entry | Exit |
|---|---|---|---|---|
| R1 | Bull put spread | SPY | 45 DTE (range 35-50); short put ~0.30 delta; long put next strike down ($1-$2 wide) | 50% of max profit, OR loss = 2x the credit, OR 21 DTE |
| R2 | R1 + volatility filter | SPY | same as R1, only when IV rank > 30 | same as R1 |
| R3 | Iron condor | SPY, QQQ, IWM (one run each) | 45 DTE; short call and put ~0.16 delta; wings $1-$2 wide | 50% of max profit, OR loss = 2x credit, OR 21 DTE |
| R4 | Bull put spread on stocks | AAPL, MSFT, AMZN, JPM, KO (one run each) | 35-45 DTE; short put ~0.25 delta; $1 wide; IV rank > 40; **no earnings before expiration** | 50% profit, OR loss = 2x credit, OR 21 DTE |
| R5 | Control: what most retail traders do | SPY | buy a 0.50 delta call, 45 DTE | +50% profit, OR -50% loss, OR 21 DTE |

R5 isn't a candidate: it's there to see how much worse the usual retail trade does under the same
costs. The "follow the flow" test is skipped: ORATS has no options-flow history (FACTS.md).

## Pass bar (Claude applies it to the CSVs)
A rule passes only if all hold, after commissions and fills:
1. 100+ trades.
2. Positive average profit per trade (expectancy), and the profit factor is above 1.2.
3. Profitable in at least 2 of every 3 calendar years, and 2008, 2020 and 2022 are each looked at
   on their own (a rule that only works in calm years fails).
4. Worst losing streak and worst drawdown, scaled to 1 contract at $2,000, stay under the
   weekly/monthly halt levels often enough to keep trading (Claude shows the numbers).
5. Not just one lucky ticker: R3/R4 need most of their tickers positive.
If nothing passes, the answer is "no trade-worthy rule yet", and that's a useful result.
