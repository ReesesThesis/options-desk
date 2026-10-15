# Facts ledger

Every outside fact the desk relies on (prices, limits, broker rules, API details) lives here with
its source and status. **VERIFIED** = checked on the official page or by the owner, with the date.
**UNVERIFIED** = from a search summary, a third-party site, or memory: never present it as fact,
and never let the owner spend money or place a trade on it until it's verified.

| Fact | Status | Source / who checked | Date |
|---|---|---|---|
| ORATS Delayed Data API is **$99/mo** list; **$49/mo** only with student discount (or partner promo pages) | VERIFIED | owner, on orats.com | 2026-10-15 |
| ORATS student plan data is ~15 min delayed; real-time needs a paid tier | VERIFIED | owner | 2026-10-15 |
| ORATS Delayed API limit 20,000 requests/month; EOD history since 2007 | UNVERIFIED | orats.com/ai-agents via search summary | 2026-10-15 |
| ORATS full history one-time $399 (FTP) | UNVERIFIED | orats.com via search summary | 2026-10-15 |
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
