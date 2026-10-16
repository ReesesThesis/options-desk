# Trailing stops on hot stocks (pre-registered 2026-10-16, before any run)

Owner's question: on "Moderna-type" stocks (hot, fast-rising names, not SPY), does an early-warning
exit (sell when a stock falls a set % from its high since we bought it) save money, or do false
alarms on ordinary dips cost more? Discretionary chart+news reading can't be backtested; a
trailing stop is the mechanical version of "it hit my marker, I'm out". The owner's own judgment
gets tested forward in his trade journal.

## Base strategy: S3 momentum (STOCK_RULES.md)
Each month-end, hold the 5 stocks with the strongest 12-1 momentum, equal weight. These are the
"hot" stocks of each month. Same costs and fills as STOCK_RULES.md.

## Stop variants (each compared with the same strategy with no stop)
- **Trailing stop X% = 15%, 20%, 25%.** After a stock is bought, track its highest close since the
  month-end decision (starting with that day's close). If a close is X% or more below that high,
  sell it at the next open; the money sits in cash.
- **Buying back:** at the next month-end, the normal ranking runs again; if the stock is still a
  top-5 name it is bought back then (this is the rule's "buy the dip"). No other re-entry.

## Two universes, because both available lists are biased, in opposite directions
- **U1 (biased AGAINST stops):** `universe_large.txt`, today's giants. Every drop in these names was
  eventually recovered, so selling on a drop looks worse than it would have in real time.
- **U2 (biased FOR stops):** U1 plus `universe_hot2020.txt`: 15 well-known 2020-21 high-flyers,
  many of which later fell 70-90%. Picked knowing they crashed, so stops look better than real.
- Reading: stops win on **both** lists = stops help; lose on **both** = they hurt; split = inconclusive.

## Pass bar for a stop level
Beats the no-stop version on total return in **both** halves (H1 to 2022-12-31, H2 from 2023) on
**both** universes. Max drawdown, number of stop-outs and how often a stopped stock was later
bought back higher are reported too. Three levels are tested, so a single narrow pass is treated
with suspicion.
