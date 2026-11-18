# GBPUSD 15m — 2026-11-17 15:30 UTC bullish agreement control

**Status:** confirmed by the Phase 2B legacy skip snapshot provided 2026-11-18. Mechanical indicator agreement; not an assertion of Cephxs parity, entry validity or profitability.

| Field | Closed-bar snapshot |
|---|---|
| Instrument | FOREXCOM:GBPUSD, TradingView 15m Bar Replay |
| Target side / New York timestamp | Bullish / 2026-11-17 10:30 |
| Captured close | 2026-11-17 **15:30 UTC**, bar 11685 |
| Candle open / close | **1.31922 / 1.32013** |
| Legacy mode | Standard, MinRun = 2 |
| Opposing bearish run length / age | **3 candles / 3 bars** |
| First / last opposing candle OPEN | **1.32003 / 1.31928** |
| Selected legacy reference | **1.32003** |
| Legacy gates | All six PASS — candle direction, level available, min run, close-through, <=60 age, no duplicate |
| Actual legacy event | **CONFIRMED** |
| First failed predicate | **CONFIRMED** (no failed gate) |
| V2 same-close confirmation level | **1.32003** |
| V2 pivot bar / born bar | 11684 / 11685 |
| V2 opposing stretch / ATR14 | **0.95×** |

**Verdict:** Both engines confirmed the same bullish close and reference level. This is **not** a V2_ONLY or LEGACY_ONLY case. The prior perception that legacy did not detect the event must not be used as a failure label; differences in plotted line visibility/retention need separate visual investigation.

Related agreement control: `research/fixtures/GBPUSD_FOREXCOM_20261117_1430Z_BULL_MATCH.md` confirmed BULL 14:30 UTC @1.31969, opposing run four candles.

Next: keep original detection rules and filters frozen; obtain a `LEGACY_ONLY` or `V2_ONLY` case from the **same snapshot** comparison registry, then validate it against independent Cephxs-only Replay at the same feed, close and level. Do not infer mismatches from chart drawings alone.
