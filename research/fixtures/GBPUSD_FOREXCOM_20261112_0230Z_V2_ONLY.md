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

## Independent Cephxs-only screenshot control — November 17, 2026, 18:17 UTC

The user hid Bandz completely and captured two zoomed TradingView screenshots showing only `cephxs / CISD [base]` on GBPUSD 15m, centered around November 12, 2026 01:00–03:00 UTC. In **both** screenshots, a **solid red horizontal CISD line** remains near **1.32745**, matching the V2 bearish level (1.32745) to visual price-axis precision. The shorter Replay screenshot includes the initial two-bar bearish break; the longer one includes later continuation. This independently rules out Bandz as the source of the red line.

The Cephxs reference Pine source (`gresl/cephxs-cisd-reference/source/cephxs-cisd-base.pine`) creates pending dotted CISD lines and confirmed **solid** lines. The visible styling is therefore consistent with a **confirmed** Cephxs bearish event. The Cephxs line originates before the break and is extended by the configured offset; the chart's line origin is NOT the confirmation clock time. We cannot assert Cephxs confirmed at precisely 02:30 UTC or 02:30:01 without a targeted forward-Replay appearance check (or logged realtime signal). The line is not sufficient to establish non-repainting live behavior.

**Updated provisional classification:** `V2_ONLY (relative to legacy)` with independently observed `Cephxs visually concordant level and direction`; precise cross-detector timestamp still **UNVERIFIED**. This supports investigating pivot-candidate structure rather than forcing the legacy engine to produce more arbitrary signals. A later bearish price move does not itself validate CISD structural correctness or trading outcome.

### Next minimal independent timing control

Keep Cephxs only, same settings; jump Bar Replay to around **2026-11-12 02:00 UTC** and advance one closed 15m bar at a time through **02:45 UTC**. Record the first endpoint where the red line is **solid**, and if it was dotted before; maintain identical feed/timeframe and avoid changing Show All Historical CISD or sensitivity. This cannot establish the exact first intrabar tick, only the first 15m Replay close where the drawing is observable. Preserve screenshots before and after that transition. Do not change either Bandz detector until the timing question is recorded.
