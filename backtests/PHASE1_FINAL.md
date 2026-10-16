# Phase 1, final round: trend and volatility filters (pre-registered 2026-10-15)

Written down **before** any of these runs, so the rules can't be tuned after seeing results.
After this round, no new strategy ideas until the owner decides what to do with Phase 1.

## The two filters (signal = list of entry dates uploaded to ORATS "Upload signal CSV")
- **Trend (T):** enter on day D only if the stock's close on D-1 was above its 50-day simple
  moving average (computed from the 50 closes ending D-1). Uses only data known before entry.
- **Volatility (V):** enter on day D only if VIX's close on D-1 was above its own median of the
  previous 252 trading days (options richer than usual, where the "options are overpriced" edge
  should be biggest). VIX is used for both SPY and KO: we have no free KO IV history, and KO's
  option prices move with the market's.

## Runs (4), each the unfiltered baseline plus one filter
| Run | Base settings | Filter | Baseline to beat |
|---|---|---|---|
| F1 | SPY put credit spread, $5 wide, no stop (= R7) | T | R7: -$51 |
| F2 | same | V | R7 |
| F3 | KO put credit spread, $1 wide, no stop (= D2) | T | D2: -$465 |
| F4 | same | V | D2 |
Everything else as before: 30/25/30 DTE, short put 0.30 (0.25-0.35), exit +0.5 / -10, hold 23,
commission 0.65 (ORATS applies its own 66% fill for 2 legs).

## Pass bar (all must hold)
1. 60+ trades.
2. Profitable after costs in **both** halves: Oct 2020 - Dec 2023 and Jan 2024 - Oct 2026.
3. Profit factor (gross wins / gross losses) above 1.2 overall.
4. Better than its unfiltered baseline in both halves (so the filter, not luck, did the work).
5. Account fit: a pass on SPY $5-wide is "valid but not tradable at $2,000" (one loss ~$400 =
   20% of the account); it would set the account size needed (~$14,000 at a 3% cap).

If nothing passes: Phase 1 ends with "no edge found"; recommend long-term investing and revisit
options with a larger account.

## Data needed (owner downloads, uploads to backtests/data/)
- SPY and KO daily prices, 2020-01-01 to today (CSV with Date and Close columns).
- VIX daily history (Cboe's free VIX_History.csv).
- ORATS's signal CSV template ("Download CSV template" under Upload signal CSV).
Claude builds the four signal files from these with `backtests/make_signals.py`.

## Amendment, 2026-10-16 (owner approved; written before any F run)
A 3-row probe (`signals/PROBE_SPY.csv`, log in `results/PROBE_SPY.csv`) showed how ORATS reads a
signal file: **each row can open its own trade while others are still open** (2 open on
2024-01-18), and the "exit" time forces a close ("Signal Exit") unless ORATS's profit target or
expiration comes first. So filtered runs hold many overlapping trades, unlike R7/D2, which held
one at a time. Comparing them to R7/D2 would be unfair, so:
- **New baselines:** F0 SPY and F0 KO enter **every trading day** (same settings, same file
  format). Pass-bar item 4 now reads "better than F0 on the same stock in both halves".
- Signal rows: entry 10:00 on D; exit 16:00 on the last trading day within 30 calendar days
  (after any 30-DTE expiration, so ORATS's own exits decide). Entries stop 30 days before the
  data ends (last entry 2026-09-15) so no trade gets a cut-short forced exit.
- Overlapping trades are correlated, so "60+ trades" is weaker evidence than it sounds; the
  two-halves and profit-factor items carry the weight. Compare per-trade averages as well as totals.
- Runs: F0 SPY, F1, F2 (SPY $5 wide, PTS OTM 5) and F0 KO, F3, F4 (KO $1 wide, PTS OTM 1); all
  other settings unchanged; ORATS date range set to All.
Everything else above stands.
