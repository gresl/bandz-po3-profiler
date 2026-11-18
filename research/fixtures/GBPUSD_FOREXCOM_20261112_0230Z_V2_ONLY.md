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

## Cephxs forward-Replay transition — November 17, 2026, 18:22 UTC

Two consecutive Cephxs-only TradingView Replay screenshots (both created 2026-11-17 18:22 UTC) establish the first **observed bar-by-bar appearance** of the solid red line at approximately `1.32745`:

| Screenshot | Latest visible 15m bar (UTC bar open) | Full bar closes | Cephxs red solid CISD |
|---|---|---|---|
| Earlier | 2026-11-12 02:00 | 02:15 UTC | **Absent** |
| After one 15m Replay step | 2026-11-12 02:15 | **02:30 UTC** | **Present**, level visually ~1.32745 |

This matches the prior V2 `BEAR CONFIRMED` record at **2026-11-12 02:30 UTC** at **1.32745**. Legacy Bandz has no matching closed event in the bounded comparison window.

**Precision boundary:** The first screenshot does not show a dotted candidate at that same level, but absence of a visible dotted line does not prove no internal pending candidate. The Cephxs source's `confirm_ok` uses the changing `close` without an explicit `barstate.isconfirmed` guard and creates a solid line on confirmation. Therefore these historical, one-bar-at-a-time screenshots **do not establish the first realtime intrabar appearance or non-repainting alert time**; they establish agreement at the 02:30 closed-bar granularity. Neither a 15-minute advantage nor a 15-minute lag between Cephxs and V2 is shown by this case.

**Classification update:** `V2_ONLY vs LEGACY`, `Cephxs visually confirmed with matching level + observed Replay closing bar at 02:30 UTC`. This is a strong positive **mechanical** reference case, not evidence of higher profitability or sufficient sample size.

Next root-cause investigation: isolate why legacy raw run-based logic does not confirm here versus V2's pivot-seeded candidate, before changing rules. Capture/obtain exact-feed OHLC if needed; do not reconstruct OHLC numerically from the image.

### Source-level missing-legacy hypotheses (not yet proved for exact candle)

Bandz legacy raw engine (see `Bandz_Po3_Profiler.pine`, around lines 1524–1570 on this branch) requires for bearish events: a red closing candle, an earlier saved **bullish-run length >= `poCisdMinRun` (configured 2)**, a close below the first run's open in Standard mode, age <=60 bars and no existing same-bar CISD. V2 instead uses pivot-seeded opposing-run candidates with **`v2rMinRun=1`**, ATR stretch gate 0.5 and separate pivot-extreme invalidation. The source-level **most economical hypothesis** is that the reference run that spawned the Cephxs/V2 02:30 close had only one qualifying bullish candle under the legacy run accounting, or a differing level; other run/reset and duplicate-bar guards remain possible.

The image alone does not yield an exact independently verifiable OHLC array or legacy internal run-state values, so no particular failed predicate should be stated as fact. Next prefer read-only C6-style probe at fixed 02:30 UTC to print legacy bullish-run length and first-run-open, duplicate-bar/age guards, V2 pivot/level and then a side-by-side rule diagnosis. Do not alter the raw detection threshold merely to make this case match.

## Proven legacy skip — 2026-11-18 18:55 UTC screenshot

The user ran the Phase 2B `4D · Legacy CISD Skip Diagnostics` branch on `FOREXCOM:GBPUSD` 15m through the target close and supplied a screenshot created 2026-11-18 at 18:55 UTC. This is **actual Pine gate-state evidence captured on the target closed bar**, not inferred OHLC from the image.

| Legacy diagnostic | Recorded |
|---|---|
| Target | Bearish / 2026-11-11 21:30 New York |
| Captured closed time | 2026-11-12 **02:30 UTC** |
| Legacy configuration | Standard / **MinRun 2** |
| Opposing bullish-run length | **1** candle |
| Opposing run age | **3** bars |
| First and last run OPEN | **1.32745 / 1.32745** |
| Selected legacy reference | **1.32745** |
| Candle bearish | PASS |
| Reference exists | PASS |
| Minimum run | **FAIL** |
| Close below reference | PASS |
| Age <=60 | PASS |
| Duplicate-event guard | PASS |
| Actual legacy signal | **NOT CONFIRMED** |
| First failed predicate | **MIN_RUN** |
| V2 same-candle confirmed level | **1.32745** |
| V2 opposing stretch/ATR | **0.90** |

The diagnostic panel explicitly marks all five other gates PASS. It is **proven** that legacy Bandz's configured two-candle minimum excludes this event; another run reference, duplicate suppression or missing close-through condition does **not** explain the skip in this recorded snapshot. V2 and isolated Cephxs previously agreed on the level and first observed 02:30 UTC completed-bar appearance.

**Decision:** Freeze this as positive mechanical parity evidence. Do **not** globally set legacy MinRun=1 from this example. Retain the original legacy detector for A/B comparison. Before changing V2's candidate acceptance rules, gather a negative control of a V2_ONLY event where Cephxs shows no corresponding confirmed CISD, then compare the same pivot/stretch predicates. An engine with more signals is not necessarily an engine with higher-quality signals. The next experiment should evaluate candidate construction and false positives, not optimize for the subsequent price decline.
