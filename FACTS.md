# Facts ledger

Every outside fact the desk relies on (prices, limits, broker rules, API details) lives here with
its source and status. **VERIFIED** = checked on the official page or by the owner, with the date.
**UNVERIFIED** = from a search summary, a third-party site, or memory: never present it as fact,
and never let the owner spend money or place a trade on it until it's verified.

| Fact | Status | Source / who checked | Date |
|---|---|---|---|
| ORATS student pricing (orats.com/student, all shown as discounts): **Trading Tools $49/mo** = web app only (Options Backtester 2,000 backtests/mo, scanners, trade builder; no API); **Delayed Data API $99/mo** = the API our code can call (20,000 requests/mo, near-EOD history back to 2007, IV rank + history, earnings history); **Historical Data $399** one-time (2007-present, 5,000+ symbols, AWS S3 download open 14 days) or $399/yr recurring | VERIFIED | owner's screenshot of orats.com/student | 2026-10-15 |
| ORATS real-time data / brokerage connection: +$50/mo on Trading Tools | VERIFIED | same screenshot | 2026-10-15 |
| ORATS Trading Tools backtester uses history back to 2007 and models fills/commissions we can set | UNVERIFIED | ORATS marketing | 2026-10-15 |
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

Research claims used in CLAUDE.md (retail option losses, Pan & Poteshman, variance risk premium)
come from paper abstracts and secondary summaries; cite them as such.
