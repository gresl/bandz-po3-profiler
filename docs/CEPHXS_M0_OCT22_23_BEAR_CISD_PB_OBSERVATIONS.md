# M0-03 — EURUSD Oct 22/23 bearish CISD/PB visual candidates

**Status:** `BEARISH_CISD_PAIR_MATCH / PB_CANDIDATE_NOT_CONFIRMED / FIRST_APPEARANCE_UNVERIFIED`.

Capture date: 2026-10-26 15:55–15:58 UTC-4. Instrument: EURUSD, 15m chart, New York timestamps per visible chart labels. Sources: Cephxs Po3 [Ultimate+] and Cephxs CISD [base] as screenshots provided in the research conversation. **Do not treat pixel estimates as exact prices or original event close timestamps.**

## Oct 22, ~03:45 NY — probable bearish PB-positive example

- `image(20261026-195528).png` — Ultimate+, chart shows two red bearish CISD-level segments around ~1.1242 and ~1.1238 immediately before/within a downward push, and Po3 framework.
- `image(20261026-195533).png` — standalone CISD [base], visually matches these two red levels and bearish displacement at the same apparent replay endpoint.
- `image(20261026-195557).png` and `image(20261026-195607).png` — indicator-free views near the Oct 22 endpoint; useful for the price-only baseline, **not sufficient alone to establish that lines persisted after an immediate same-endpoint reload**.
- The later lower red level is a **PB candidate** based on the sequence and display; no exact level, line-width semantics, parent CISD-zone predicate, or first-knowable close has been established. Strong subsequent bearish motion is not itself proof of PB classification.

## Oct 23, ~04:30 NY — second bearish example

- `image(20261026-195820).png` — Ultimate+ shows historical bearish red marks, near ~1.1209 and ~1.1194, within ongoing bearish structure.
- `image(20261026-195824).png` — standalone CISD [base] shows visually corresponding red marks at the same apparent endpoint.
- These screenshots appear to be from a **later replay position** than the Oct 22 captures; do not treat the overall six-image series as a controlled unchanged-endpoint toggle test.
- The Oct 23 case is **not established as a PB-negative control**; it may contain an additional PB candidate, pending source rule/width identification.

## Findings and next narrow test

**Pass:** bearish directional/price-area agreement between Ultimate+ and standalone CISD [base] in two example sets.

**Not yet passed:** exact PB classification, per-event close/time, parent-zone predicate, same-endpoint toggle stability for Oct 22, no-repaint/forward-only establishment.

To upgrade Oct 22 to an acceptance candidate: use exact same feed/profile (`15m → 4H` for Ultimate+) and settings, Replay one 15m bar at a time around the initial/lower red line, recording the immediately prior candle, the first candle-close at which each red mark is visible, and one immediate same-endpoint hide/show of both indicators. Note that TradingView bar labels are bar opens; calculate the confirming close separately. Record exact price with crosshair/Data Window. Negative control should be explicitly an ordinary CISD without a thin PB after sufficient follow-through; do not designate Oct 23 negative without checking.

No Bandz code/threshold change recommended from this evidence alone.

## Oct 26, 16:04–16:05 UTC-4 — Oct 22 same-endpoint visibility toggle retest

Evidence screenshots (capture timestamp shown in images):
- `image(20261026-200429).png`: CISD [base] ON; red bearish level at approximately 1.1242 near the Oct 22 02:30 candle.
- `image(20261026-200436).png`: Po3 Ultimate+ ON; corresponding red bearish level at the same market position.
- `image(20261026-200456).png` and `image(20261026-200502).png`: indicators OFF/clean chart at replay endpoint.
- `image(20261026-200514).png`: Po3 Ultimate+ restored, red level persists.
- `image(20261026-200525).png`: CISD [base] restored, red level persists.

Trader reports repeated OFF/ON/OFF/ON of both indicators without changing replay endpoint. Visible reference levels agree to screenshot precision, allowing for different chart zoom and scaling.

**Result: PASS — reproducible bearish CISD level after recalculation at a fixed replay endpoint.**

**Scope limitation:** Does not establish the event's first knowable candle close, no future-data/repainting globally, specific PB-positive classification, or equality of underlying engine implementation. The lower PB-candidate line seen in later-Oct-22 screenshots is not yet proven to exist at this endpoint; do not use this pass to claim PB parity. Exact level from Data Window/crosshair remains unrecorded.

**Next controlled action:** replay forward one 15m candle at a time from before appearance of the candidate *second/lower* bearish mark and record first signal appearance (chart bar *open* label versus actual signal-confirmation *close*), whether that line represents PB in Ultimate+ and CISD [base], and its exact level. Record both snapshots at the same close and repeat a same-endpoint toggle for the candidate line.

## Oct 26, 16:17 UTC-4 — Oct 22 dual-line same-endpoint comparison

New matched screenshots:
- `image(20261026-201707).png` — Po3 Ultimate+.
- `image(20261026-201715).png` — standalone CISD [base].

Both show an earlier upper red bearish line approximately 1.1242, plus a subsequent paler/lower red bearish line approximately 1.1238. The latter is drawn from the vicinity of the Oct 22 03:00 NY bar, with the newest visible large bearish bar at approximately 03:15 NY (chart bars are labelled by opening time). Both indicators depict the lower line at the same approximate level and anchor; pixel evidence only, exact quote and timing still to be crosshair-verified.

**Result: PASS — paired upper and lower red-level visual agreement at this later replay endpoint.**

**Unresolved:** the screenshot does not show the immediately preceding replay endpoint, so first *observability* and confirm close are not known; a historically drawn line can be anchored before first visibility. The fact that CISD [base] also draws the lower level prevents inferring that the lower mark is PB-specific. No same-endpoint OFF/ON for the *lower* line is included here. Therefore the PB-positive tag remains a hypothesis, not accepted ground truth.

**Next test:** capture one step before the lower line first becomes visible and the first step showing it; record exact time, date, open-labelled bar vs closing time, source-indicator visibility, line color/weight and exact red level. Then optional lower-line toggle at that identical endpoint. Avoid tuning PB rules from these screenshots alone.

## Oct 26, 16:23–16:24 UTC-4 — Oct 22 adjacent replay bars, upper red-line transition

Pair A (capture 16:23):
- `image(20261026-202317).png` — Po3 Ultimate+.
- `image(20261026-202324).png` — CISD [base].
- Last displayed bar appears to be Oct 22 **02:15 NY bar** (15m opening-time label; presumed close 02:30 NY in bar-close replay).
- The later continuous horizontal bearish line near ~1.1242 is **not yet solidly drawn** in either. CISD [base] has a *faint red dotted segment* at approximately the same price: do not say there was no candidate/reference visible at all.

Pair B (capture 16:24):
- `image(20261026-202412).png` — Po3 Ultimate+.
- `image(20261026-202415).png` — CISD [base].
- Last displayed bar appears to be Oct 22 **02:30 NY bar** (presumed close 02:45 NY).
- Both now show a **solid red horizontal level** near ~1.1242, drawn across the preceding green/last bearish candles; last black candle closes below the level.

**Result:** PASS for matched **solid-line emergence** across adjacent replay bars at screenshot precision; first observed as solid at the 02:30-opening candle / presumed 02:45 close. This tests line visibility timing, **not** the first existence of the faint/red dotted precursor, underlying PB signal semantics, or absence of live-bar flicker. The **lower** ~1.1238 line from the later 16:17 captures has **not** been bracketed by these four screenshots; this is an **upper-line** transition only. Bar timestamps must be validated with crosshair/Data Window if exact close is required.

**Next:** advance 02:45, 03:00 and 03:15 15m bars (or stop when lower ~1.1238 solid reference first appears); save one immediately-before and one first-appearance pair on Ultimate+ and CISD [base], with the same replay endpoints. No rule changes.
