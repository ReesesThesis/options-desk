# Facts ledger

Every outside fact the desk relies on (prices, limits, broker rules, API details) lives here with
its source and status. **VERIFIED** = checked on the official page or by the owner, with the date.
**UNVERIFIED** = from a search summary, a third-party site, or memory: never present it as fact,
and never let the owner spend money or place a trade on it until it's verified.

| Fact | Status | Source / who checked | Date |
|---|---|---|---|
| ORATS student pricing (orats.com/student, all shown as discounts): **Trading Tools $49/mo** = web app only (Options Backtester 2,000 backtests/mo, scanners, trade builder; no API); **Delayed Data API $99/mo** = the API our code can call (20,000 requests/mo, near-EOD history back to 2007, IV rank + history, earnings history); **Historical Data $399** one-time (2007-present, 5,000+ symbols, AWS S3 download open 14 days) or $399/yr recurring | VERIFIED | owner's screenshot of orats.com/student | 2026-10-15 |
| ORATS real-time data / brokerage connection: +$50/mo on Trading Tools | VERIFIED | same screenshot | 2026-10-15 |
| ORATS Custom Backtester (dashboard.orats.com/backtesting/custom) data starts 2020 (owner); it is the intraday backtester (entry time of day), fields: DTE target/min/max, delta target/min/max, leg 2 "pts OTM" from leg 1, Exit Profit/Loss % min/max, Trade % Slippage (default 66), Commission $/contract (default 0.65), Max Hold Days, wide bid-ask filter, Upload signal CSV for custom entry dates. No IV-rank or earnings filter seen on that screen | VERIFIED | owner's screenshot | 2026-10-15 |
| ORATS Custom Backtester: leg 1 DTE target cannot exceed 30 days | VERIFIED | owner (error message) | 2026-10-15 |
| Whether Trading Tools also has an end-of-day backtester with data back to 2007 | UNVERIFIED | ORATS marketing; ask ORATS | 2026-10-15 |
| ORATS "Trade % Slippage": slippage charged on entry AND exit as a % of the bid-ask width (75 = three quarters of the spread paid each side); defaults 75/66/55/53 for 1/2/3/4+ legs. ORATS "Exit Profit/Loss %" takes decimals (-0.5 = -50%, 0.5 = 50%) | VERIFIED | owner's screenshots of the tooltip and field hints | 2026-10-15 |
| ORATS Custom Backtester **ignores the "Trade % Slippage" field** and always uses its leg-count default: 2 legs 66%, 3 legs 56%, 4 legs 53% (1 leg 75%). Fill formula: buy = bid + (ask-bid) x slip, sell = ask - (ask-bid) x slip, so at 66% each leg fills 16% of its own bid-ask width worse than the mid, on entry and again on exit; $0.65/contract commission on top (matches our logs). Otto called this a bug and suggested reporting it to support@orats.com | VERIFIED (identical results at 0/50/75; ORATS's Otto agent, which says it "can be wrong") | owner's screenshots | 2026-10-15 |
| Whether ORATS Exit Profit/Loss % is measured against the credit received (vs. max risk) | UNVERIFIED | read the Exit Profit/Loss (i) tooltip | 2026-10-15 |
| Correction: an earlier entry said the $49 student price was for the Delayed Data API. Wrong: $49 is Trading Tools (no API). | - | - | 2026-10-15 |
| ThetaData free tier: 1 year EOD options, ~20-30 requests/min; Value ~$40/mo (history from 2020) | UNVERIFIED | thetadata docs/pricing via search summary | 2026-10-15 |
| Schwab Trader API - Individual: must **request access** to the product before creating an app | VERIFIED | owner, developer.schwab.com | 2026-10-15 |
| Schwab app needs both "Accounts and Trading Production" and "Market Data Production" | UNVERIFIED | memory | 2026-10-15 |
| Schwab callback URL `https://127.0.0.1` accepted; refresh token lasts 7 days | UNVERIFIED | memory / developer community | 2026-10-15 |
| PDT $25k rule removed: SEC approval 2026-04-14, effective 2026-06-04, brokers have until 2027-10-20 | UNVERIFIED (secondary) | Schwab advisor article via search summary | 2026-10-14 |
| Webull: spreads need a margin account with $2,000+ equity | UNVERIFIED | memory | 2026-10-15 |
| Webull: GTC allowed on multi-leg option orders; stop orders on spreads unreliable | UNVERIFIED | memory | 2026-10-15 |
| Webull options fees: $0 commission + per-contract regulatory/exchange fees (config uses $0.60/leg estimate) | UNVERIFIED | memory | 2026-10-15 |
| Unusual Whales API $150-750/mo; dashboard ~$48/mo | UNVERIFIED | third-party comparisons via search | 2026-10-14 |
| Phase 0 env vars present (lengths only checked, values never printed): SCHWAB_APP_KEY, SCHWAB_APP_SECRET, SCHWAB_REFRESH_TOKEN, SCHWAB_REFRESH_ISSUED, SEC_USER_AGENT. ORATS_TOKEN not set (not needed yet) | VERIFIED | Claude, cloud session | 2026-10-15 |
| SCHWAB_REFRESH_ISSUED is entered as MMDDYYYY (10152026), not YYYY-MM-DD; `desk.py status` crashed on it. Code now accepts both; status reads "7 day(s) left" (renew by 2026-10-22) | VERIFIED | `desk.py status` | 2026-10-15 |
| Schwab Trader API works from the cloud with our app: token refresh, quotes, option chains, daily price history (so "Market Data Production" is enabled on the app) | VERIFIED | `desk.py context KO`, `fetch_prices.py` | 2026-10-15 |
| SEC EDGAR works from the cloud with SEC_USER_AGENT (CIK lookup + submissions). KO's last watched filing is a Form 4 on 2026-08-24; in the last 30 days only Form 144s and a 25-NSE (2026-09-22), which `filings` doesn't watch | VERIFIED | `desk.py filings KO --days 120`, raw submissions | 2026-10-15 |
| Schwab KO quote at 6:04 pm ET 2026-10-15 (after hours): last $91.98, bid $91.80 / ask $91.98, prior close $91.78, day open $93.145, high $94.10 (= 52-wk high), low $91.715, volume 19.66M. **Regular-session close 2026-10-15: $92.00** (Schwab daily history). Schwab's `closePrice` field is the *previous* day's close | VERIFIED (Schwab) / **Webull match: PENDING, owner to compare** | Schwab API | 2026-10-15 |
| Schwab KO Nov 20 2026 chain, after hours 2026-10-15 (bid/ask, IV, delta, OI): 87.5P 0.78/0.97, 22.1%, -0.229, OI 3,487; 90P 1.47/1.65, 21.0%, -0.363, OI 2,091; 92.5P 2.47/2.72, 23.0%, -0.521, OI 510; 90C 3.60/4.05, 21.0%, 0.637, OI 9,362; 92.5C 2.28/2.45, 23.0%, 0.479, OI 5,085; 95C 1.26/1.49, 22.6%, 0.333, OI 4,058. Schwab gives calls and puts at a strike the same IV | VERIFIED (Schwab) / **Webull match: PENDING, owner to compare at the open** | Schwab API | 2026-10-15 |
| KO ATM IV by expiry (Schwab, after hours, `context KO`): Oct 23 18.9%, Oct 30 24.5%, Nov 6 22.0%, Nov 13 27.1%, Nov 20 23.0%. The Nov 13 point (and its $5.34 straddle above Nov 20's $4.97) looks like a stale after-hours quote: recheck in market hours before using it | VERIFIED as returned; Nov 13 **SUSPECT** | Schwab API | 2026-10-15 |
| KO Q3 2026 earnings date: not yet in SEC filings. Last four earnings 8-Ks: 2025-10-21, 2026-02-10, 2026-04-28, 2026-07-28. The IV jump from the Oct 23 to the Oct 30 expiry hints at a date between them | **UNVERIFIED / MISSING**: check KO investor relations | SEC 8-K item 2.02 dates; Schwab IVs | 2026-10-15 |
| Schwab daily price history (`/pricehistory`, daily) is **split-adjusted, not dividend-adjusted**: XLU shows no ~50% drop across its late-2025 2-for-1 split (44.58 on 2025-11-24, 43.18 on 2025-12-18). SPY 2020-03-16 -10.9% and VIX 82.69 match the well-known crash-day closes | VERIFIED (internal consistency); dividend adjustment **UNVERIFIED** (looks unadjusted, not confirmed against Schwab docs) | `backtests/fetch_prices.py` | 2026-10-15 |
| Schwab $VIX daily history has bars on some market holidays (10 since 2025, e.g. 2025-07-04, 2025-11-27) and is missing 2019-11-29 and 2021-05-14. `fetch_prices.py` keeps only SPY trading days. Source is Schwab, not Cboe's VIX_History.csv named in PHASE1_FINAL.md | VERIFIED | `fetch_prices.py` | 2026-10-15 |

Research claims used in CLAUDE.md (retail option losses, Pan & Poteshman, variance risk premium)
come from paper abstracts and secondary summaries; cite them as such.
