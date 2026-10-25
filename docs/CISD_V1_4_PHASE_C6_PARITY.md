# Phase C6 — Raw CISD / structural parity audit (research only)

## Question

For EURUSD 15m on 2026-09-21, Cephxs appears to mark a bearish CISD at **09:30 New York** while the Bandz event-time audit records confirmation **09:45 New York**. These may be two timestamps for the **same 09:30–09:45 candle**, not a detector lag. This branch captures the evidence required to test that hypothesis without altering the detector.

## Pine changes

- Added `Research: raw CISD / structural parity details`, **OFF by default**; enables exactly six appended audit rows.
- Freeze each raw confirmed event's `time` (candle OPEN), `time_close` fallback (confirmation CLOSE, existing), `close`, the original opposing run's first candle open and the last opposing candle's open/high/low/time.
- The selected CISD level remains the unmodified Bandz Standard/Sensitive delivery open; displayed breach distance is measured in `syminfo.mintick`.
- Show explicit `RAW confirmed` separately from `QUALIFIED/REJECTED (configured gates)`. Eligibility is the existing at-confirmation snapshot and may differ when filters are enabled.
- The last opposing candle is an **order-block reference only**. It is NOT claimed to be a valid TTrades/ICT Propulsion Block. A PB requires another established OB, a revisit and confirming expansion/displacement; no such detector is introduced here.
- Add six rows after the existing audit and optional 16/32-bar outcomes. With the checkbox off, the audit table retains its previous size.

**No modifications** to CISD triggers, C2 linkage, standard/sensitive settings, FVG engine, draw eligibility, legacy rendering, indicator alerts, Po3, webhook fields or 16/32-bar outcome logic.

## Manual acceptance (TradingView — Pine v6)

1. Copy `Bandz_Po3_Profiler.pine` from **this C6 branch**. Compile in TradingView. Do not copy the PR diff.
2. Choose `FOREXCOM:EURUSD`, chart **15m**, Po3 `15m → 4H`, timezone **America/New_York**, the previous saved Phase C research template, `CISD = All + C2 highlighted`.
3. Check `Research: event-time audit panel`, `Research: raw CISD / structural parity details`, and `Research: audit selection mode = Fixed NY close`.
4. Enter `Research: fixed CISD close NY = 2026-09-21 09:45`. Replay through the bearish event confirmation. **Expected if the same 15m candle:** C6 RAW candle OPEN NY is `2026-09-21 09:30`, C6 RAW confirmed CLOSE NY is `2026-09-21 09:45`; the existing CISD level remains **1.14804** (same feed/settings as earlier screenshots). If times do not match, record the actual values, do not reinterpret them.
5. In Cephxs at the *same replay endpoint*, identify whether the 09:30 label is attached to the candle opening at 09:30. Compare the exact **price level**, not just label timestamps. One candle / two timestamp conventions would remove a timing discrepancy, but different levels would still require separate investigation.
6. Capture **one paired screenshot** of Cephxs and Bandz for that replay point, plus a readable C6 panel close-up showing raw open/close, break-close/ticks, first/last opens, last opposing candle, and qualified/rejected result. An optional +1 candle checks immutable raw fields.
7. Regression: fixed bullish 2026-10-16 10:00, fixed bullish 2026-10-08 08:15, with audit offset/legacy modes; confirm no changes to existing event-time audit rows or +16/+32 outcomes.
8. Toggle C6 checkbox OFF: prior visual appearance and table size should return. Verify no Pine runtime warnings.

## Interpretation and next step

The frozen **raw CISD** is a close-through an opposing delivery-open under Bandz's original algorithm. **Structural qualification** is a separate optional screening layer, not part of the definition of the raw trigger. The first/last opposing reference prices are diagnostic and not evidence of a validated PB. Do not change signal, entry, stop or quality thresholds based on this one replay.

After confirming candle identity/price parity, the next independent experiment will specify a genuine PB model: parent OB, return into parent, opposing revisit candle, mean threshold, displacement/hold and invalidation, with event-time separation from later evidence.

**Status:** Source upload and static anchor checks completed; TradingView compilation and manual Replay pending. Draft PR only.