# PB-A — Cephxs reference capture before access expires

**Priority:** collect observable proprietary indicator behavior while Cephxs is available; do not attempt to obtain its hidden source or bypass expiration.
**Date established:** 2026-10-26 (New York EDT / UTC-4). Possible access end 2026-10-31, possibly earlier.
**Repository baseline:** PB research spec PR #11; Phase C6 parity research PR #10. No code changes required for this capture.

## Setup (do not retune during sample collection)

- TradingView chart symbol: `FOREXCOM:EURUSD` (verify exact prefix in both charts).
- Chart: 15m; Po3 HTF profile: 4H; timezone: `America/New_York`; candles standard (not Heikin Ashi).
- Record *both* indicator names and full Inputs screenshots, especially Cephxs PB/CISD visibility, label mode, displacement and C2 filters, and Bandz `Research: audit selection mode`.
- Keep market-data feed, replay date, replay endpoint, timezone and viewport range identical when comparing. A 15m candle labeled 09:30 OPEN only closes/qualifies at 09:45.
- Bandz fixed-event audit from an older date can show `FIXED EVENT NOT SELECTED / NOT FOUND in retained history`; switch to `Newest offset`, offset `0` or `1`, for current-case inspection. This changes *only which event is inspected*; do not change CISD sensitivity or gate configuration as part of a capture.
- Zoom to show 20–40 pre-event chart candles and ~8–16 following candles when available. If the parent OB is older, use an additional context-wide screenshot.

## Capture priority and minimum dataset

**Priority 0 — Preserve settings today:** Save screenshots of *all* Cephxs Inputs pages that control PB/OB/CISD and the selected profile. Write down indicator exact title/version where visible. Capture its PB legends and drawn sample patterns. Preserve these locally.

**Priority 1 — 3–5 marked PB examples plus at least 2 non-PB controls:** Start with 2026-10-26 EURUSD to inspect today's short, then revisit 2026-09-21, 2026-10-08, 2026-10-16 EURUSD (these are known CISD study windows, **not prevalidated PB examples**). If they contain no unequivocal PB marks, search a different session/instrument. Include bullish and bearish examples; do not cherry-pick only winners. One GBPUSD example is desirable.

For each **Cephxs-labeled PB**:
1. Capture Cephxs chart at the **first replay point where the PB becomes visible**, including bottom axis time and right price scale. If possible, also capture one closed bar before and 1, 4, 16 bars after. Record whether the mark survives.
2. Capture an identical Bandz screenshot at the same replay endpoint. Disable *only visual clutter* (research Full labels, excess projection levels), not detection gates, unless documenting the change.
3. Mark which prior candle/run is the apparent **parent OB** and which revisit candle is the **PB candidate**; record exact NY **candle opening time** for each and the PB level (opening price) and 50% BODY threshold. If uncertain, write `unknown`, not a guessed parent.
4. Record the first **displacement/departure candle close**, and whether an FVG or CISD appeared *at that close* versus on later bars.
5. If there is no clear parent OB, record `CEPHXS PB — parent not obvious`; this is a valuable false-positive test against our strict model.

For **non-PB controls**: save a lookalike opposing candle/FVG/CISD that Cephxs does **not** label PB, with same context. This prevents fitting the detector solely to the winners.

## Minimal row schema (one row per PB or control)

| Column | Value / convention |
|---|---|
| sample_id | E.g. EU-20261026-01 |
| ticker/feed | FOREXCOM:EURUSD |
| chart_tf/profile | 15m / 4H |
| zone_time | America/New_York |
| direction | BULL / BEAR |
| cephxs_pb_visible | yes / no / uncertain |
| parent_ob_open_ny | YYYY-MM-DD HH:mm or unknown |
| pb_candidate_open_ny | YYYY-MM-DD HH:mm or unknown |
| cephxs_first_seen_close_ny | YYYY-MM-DD HH:mm or unknown |
| pb_open_price | decimal or unknown |
| pb_body_mean | (open+close)/2 or unknown |
| departure_close_ny | YYYY-MM-DD HH:mm or unknown |
| same_bar_cisd | yes / no / uncertain |
| same_bar_fvg | yes / no / uncertain |
| later_1_4_16 | persists/invalidated/new information |
| screenshot_refs | filenames, e.g. EU-20261026-01-cephxs.png |
| notes | key OB/CRT context and ambiguities |

## Today's first *context/control candidate* (NOT a proven PB)

- EURUSD Monday 2026-10-26, two TradingView screenshots captured at about 11:39 and 11:41 UTC-4.
- Broad bearish movement toward horizontal 1.11821 and below; trade-rectangle/level interpretation requires MT5 fills and chart details.
- Bandz header shows `C2 Phase (live)` while Cephxs shows `No Phase` at near-same clock time; classify as **phase-state comparison only**.
- Bandz event audit panel lower right shows older fixed-event selection is not found in retained history; use Newest offset during this test.
- No demonstrated Cephxs-labeled PB / parent OB from these two screenshots alone. Preserve as a potential **negative PB control** or later positive only if the label is unambiguously documented.
- For a trade verdict, obtain ticket entry/exit timestamps, fill prices, SL/TP, instrument, chart TZ, and rationale as known **before** execution; screenshots after the move are not sufficient.

## After access expires

Keep immutable screenshots/videos and the observation log in local storage; do not claim exact Cephxs code parity from reverse interpretation. Continue PB-A1 (causal parent OB snapshots), PB-A2 (revisit and later PB confirmation), PB-A3 (frozen visual comparisons and outcomes). Use only evidence known by each candle's close to decide eligibility.
