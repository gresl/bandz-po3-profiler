# GBPUSD 15m — 2026-11-12 02:30 UTC V2_ONLY bearish candidate

**Status: source-level mechanical evidence; Cephxs parity unverified.**  
Snapshot: user TradingView screenshot created 2026-11-17 18:10 UTC (historical Bar Replay).

## Recorded state at replay

| Dimension | Observation |
|---|---|
| Feed | FOREXCOM:GBPUSD (reported prior, visually GBPUSD 15m) |
| Direction | BEAR |
| V2 first-known close | 2026-11-12 02:30 UTC |
| V2 confirmation close | 2026-11-12 02:30 UTC |
| V2 level | 1.32745 |
| V2 stretch / ATR14 | approximately 0.90 |
| V2 state | CONFIRMED |
| Paired legacy event | None in retained comparable intersection; class V2_ONLY |
| Comparison table | EXACT=8, LEVEL=0, TIME=0, V2_ONLY=6, LEGACY_ONLY=0, STAMP=0 |
| Replay endpoint | END OPEN, close endpoint 2026-11-12 02:45 UTC |
| Cephxs indicator | User states enabled; a short red line near V2 price is visible, but origin cannot be attributed without single-indicator isolation |
| Price aftermath | Large bearish continuation visible; **not validation of setup correctness** |

## Important interpretation

The V2-only label means *relative to internal legacy Bandz event history only*. It is not Cephxs-only and does not establish correctness. V2's first-known and confirmation timestamps are both 02:30 UTC, meaning it registered and confirmed after the 02:15–02:30 bar closed. The 02:30–02:45 endpoint bar is currently OPEN. The Cephxs horizontal segment may be drawn on an earlier origin bar; drawing anchor is not the exact moment of confirmation.

## Next minimum experiment

1. **Do not advance Replay or change any input values.**
2. Temporarily **hide the entire Bandz indicator instance**. Keep only Cephxs CISD [base] enabled at original defaults, especially Show All Historical CISD = OFF. Take a cropped screenshot 2026-11-12 01:15–03:15 UTC with price axis, to determine whether the red line survives and which bar/price it corresponds to.
3. Restore the Bandz instance and optionally hide Cephxs; take the matching side-by-side-by-screenshot if ambiguity remains.
4. If Cephxs red line remains, inspect its precise level and when it first appears during controlled forward Replay, distinguishing candidate dotted from confirmed solid.
5. Before asserting 'valid CISD', inspect true originating stretch, pivot, OHLC, C2/CRT relationship, contextual market condition and stop/entry geometry; comparison to a matching visual line alone is not correctness.

No detector code or sensitivity changes are authorized by this single event.
