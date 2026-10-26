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
