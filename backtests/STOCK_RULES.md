# Stock rules: three tests (pre-registered 2026-10-16, before any data for them was pulled or run)

Owner's direction after Phase 1 ("we're moving from options to holding"): find out, on history,
whether any simple stock rule beats just holding. Run here by `backtests/stock_rules.py` on Schwab
daily prices (split-adjusted, **not** dividend-adjusted: every strategy and benchmark uses price
returns, so all are short their dividends alike; SPY's yield was roughly 1.3%/yr, **UNVERIFIED**).

## Common rules
- Period: first possible decision (after each rule's lookback) through 2026-10-15.
- **Halves:** H1 = start through 2022-12-31; H2 = 2023-01-01 through 2026-10-15.
- Decisions use closes up to day D; trades fill at the **open of D+1** (no peeking).
- Cost: 0.05% of the amount traded on every buy and sell (spread/slippage); $0 commission.
- Cash earns **0%** (conservative: T-bills paid several % in 2023-2025, which would help S1).
- Taxes ignored (frequent selling in a taxable account would cost more; noted, not modeled).

## S1: SPY trend (200-day)
Hold SPY while its close is above its 200-day simple average; otherwise hold cash. Checked daily.
Benchmark: hold SPY.

## S2: Sector rotation
On the last trading day of each month, rank the 11 sector ETFs (XLB XLC XLE XLF XLI XLK XLP XLRE
XLU XLV XLY) by their return over the past 63 trading days (~3 months); hold the top 3, equal
weight, until the next month's decision. Benchmark: hold SPY.

## S3: Big-stock momentum
Universe: about 100 of the largest US stocks (`backtests/universe_large.txt`, written today).
On the last trading day of each month, rank stocks by "12-1 momentum": return from 252 trading
days ago to 21 trading days ago (the classic academic measure; skipping the last month avoids its
short-term reversal). Hold the top 5, equal weight, until next month. A stock is eligible only once
it has 273 trading days of data.
Benchmarks: (a) hold SPY; (b) **equal-weight all eligible universe stocks, rebalanced monthly**.
**Survivorship bias, stated now:** the list is today's giants, picked knowing they became giants.
That flatters any rule run on it, so S3 must beat (b), which has the same bias; beating SPY alone
proves nothing.

## Pass bar (each rule, after costs)
1. Total return beats its benchmark(s) in **both** halves.
2. Report alongside (not part of pass/fail): yearly returns, max drawdown, number of trades.
A rule that fails is recorded and not tweaked. A rule that passes goes to the owner as a candidate
for the 10-20% "satellite"; the core stays in an index fund either way.
