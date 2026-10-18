# CISD v1.4 — Event-time eligibility audit: implementation specification

**Branch:** `feature/cisd-v1.4-event-time-audit`, based on `feature/cisd-v1.4-phase-b-display-filters` (draft PR #5).
**Status:** **implemented in Pine, awaiting TradingView compilation and Bar Replay verification**. Source commit: `9ddf2c70b78f27cc15ecad2488c58f44b1097db9`. This is research instrumentation, not a verified trading signal. GitHub source read-back passed; the GitHub connector cannot compile Pine or test TradingView's chart runtime.

## Purpose and invariants

Capture the eligibility decision at the **original CISD confirmation candle close**. Do not allow later FVG creation, qualified C2 closure, or a subsequent reclamation to retroactively qualify that earlier event. Preserve the existing raw CISD detector, Po3 C1–C4 state machine, original charts, Phase B drawing filters, and all alert/trading behavior.

Phase A already froze `c2SweepAtConfirm`, `c2QualifiedAtConfirm`, `bodyToRangeAtConfirm`, `bodyToAtr14AtConfirm`, `directionalCloseAtConfirm`, and `alignedFvgAtConfirmBar`. **Do not replace this proven snapshot logic**. The missing part is a per-event audit record and a discoverable panel, independent of the aggregate bottom-left counts.

## Required event fields

Extend `PoCisdEvent` with:

```pine
bool  auditCaptured
bool  auditContextPass
bool  auditC2Pass
bool  auditDisplacementPass
bool  auditFvgPass
bool  auditCombinedPass
int   auditFvgBornTime
float auditFvgTop
float auditFvgBot
```

At the end of the existing confirmed-bar `poResearchFvgEnabled` update block, after **both** same-bar three-candle FVG detection and at-confirmation association, and only if a new CISD was recorded on `bar_index`:

1. Check `not ev.auditCaptured` before assigning any audit field.
2. If `alignedFvgAtConfirmBar` is not `na`, locate the confirmed same-direction `PoResearchFvg` with the matching `bornBar`, and ensure `bornTime <= ev.confirmTime`. Copy `bornTime`, `top`, `bot`. If no match, leave these values `na` but **surface this discrepancy**.
3. Freeze `auditContextPass = poCisdBaselineContextPass(ev)`.
4. Freeze `auditC2Pass` using the *selected* Phase B C2 mode and the existing frozen `c2SweepAtConfirm` / `c2QualifiedAtConfirm` flags.
5. Freeze `auditDisplacementPass = poCisdDispPass(ev)`, regardless of whether that requirement is enabled, and `auditFvgPass = not na(ev.alignedFvgAtConfirmBar)`.
6. Freeze `auditCombinedPass = auditContextPass and auditC2Pass and (not poCisdQualDisp or auditDisplacementPass) and (not poCisdQualFvg or auditFvgPass)`. Mark `auditCaptured := true`, including when there is **no** qualifying FVG.
7. **Never** change the audit fields as later candles arrive. The existing `c2ClosedAt`, `alignedFvgLaterBar`, and `invalidatedTime` remain separate outcome data.

Pine input changes trigger full-script recomputation: changing thresholds can legitimately produce a different *historical* confirmation-time verdict for that configuration. Advancing Replay **without** changing inputs must not.

## Optional UI

Add to `PO_G8B`:

```pine
bool poCisdAuditOn = input.bool(false, "Research: event-time audit panel", group = PO_G8B)
int poCisdAuditOffset = input.int(0, "Research: audit newest-event offset", minval = 0, maxval = 19, group = PO_G8B)
```

Allocate an optional bottom-right 2-column table. On `barstate.islast` in the same research mode as Phase B, pick `poCisdEvents.get(size - 1 - min(offset, size - 1))`, with an empty-history guard, and display:

- Identity: `syminfo.tickerid`, direction, `confirmTime` (CISD **close** in `poTz`), `startBar`, `level`. Together these identify an event within one loaded feed/run; not a globally durable ID.
- **THEN:** associated C2/sweep/closed-at-confirmation, three displacement ratios, at-confirmation aligned FVG **formation time and top/bottom**, and context/C2/displacement/FVG pass flags.
- **AT CLOSE:** immutable combined eligibility, plus a MATCH/DRIFT comparison against recalculating Phase B eligibility from the frozen original event fields.
- **LATER (outcomes):** eventual `c2ClosedAt`, `alignedFvgLaterBar`, and `invalidatedTime`, clearly separate from the at-close decision.

A MATCH validates internal predicate consistency, **not** deterministic replay, predictive accuracy or profitability. The event's **visibility now** can change with invalidation/recency/caps; this is not an at-close eligibility change. Do not use a later field in the confirmation-time pass calculation. All features default OFF and must leave ordinary drawings unchanged.

## Replay validation

On the same EURUSD 15M → 4H feed, timezone America/New_York, confirm:

1. **Compile** Pine v6. Check runtime/object limits when the audit panel is ON and OFF.
2. **Oct 16 bearish CISD near NY 08:15:** select the record with the offset input. If no aligned FVG existed then, display `none` both before and after the +1 later FVG appears; only the retrospective field may change.
3. **Oct 8 bullish live-C2 CISD:** `C2 THEN` remains provisional after the later valid C2 close; eventual closure appears only as retrospective context.
4. **Same-bar aligned FVG:** formation offset is 0 and its already-confirmed boundaries stay fixed.
5. **With audit toggled:** raw CISD events, Po3 phases, Phase B eligible/drawn counts, and legacy chart drawings must remain identical at equal endpoints.
6. **Offset + retention:** exercise 0, 1, 19, fewer-than-20 and the 100-event cap; empty registry must not throw. Check that an event with no FVG gets `auditCaptured=true` immediately.

**No trade signals or alerts; no Cephxs parity or validated predictive edge implied.**

## Implementation notes and practical TradingView procedure (2026-10-18)

- The audit capture runs only in the opt-in **All + C2 highlighted** research mode, on a confirmed chart bar, **after** FVG formation, original-window association, confirmation-time association, and later-FVG bookkeeping. A new event with no aligned FVG must still be snapshotted as `auditCaptured=true`, `auditFvgPass=false`.
- The optional panel is enabled by **4B · CISD structural research → Research: event-time audit panel**, initially OFF. **Research: audit newest-event offset** selects the newest confirmed event (`0`), previous (`1`), etc. Offset `19` is clamped for shorter retained histories.
- Panel location: bottom-right, 2 columns. **THEN** shows frozen C2 and FVG confirmation-time evidence, metrics and gate results. **AT CLOSE** shows the frozen combined verdict. **LATER** shows retrospective closure/FVG/invalidation observations. A separate **MATCH/DRIFT** field compares the saved verdict with a fresh calculation *only from the event's frozen inputs*. A separate **MISSING FVG RECORD** warning flags an at-close FVG pointer whose immutable formation details could not be recovered.
- The panel is display-only. Existing raw detection, sequence profiling, legacy overlays, Phase B selection/drawing code, aggregate counts and alerts have not been edited by this commit. Any changed history on **input edits** is an expected TradingView full-script recomputation; unchanged inputs during Bar Replay must not change original snapshots.

### Replay checklist for the operator

1. Copy `Bandz_Po3_Profiler.pine` from **this branch** into a separate TradingView Pine v6 indicator; compile. Record exact errors/warnings and confirm no resource-limit problems when the new panel is OFF.
2. Use the same `EURUSD` feed as the earlier tests, **15-minute chart → 4H Po3 profile**, `America/New_York` timezone. Set **CISD → All + C2 highlighted**, `Research: retain events = 100`, and `Research: event-time audit panel = ON`. Keep the existing Phase B settings unchanged when comparing with the previous branch.
3. Around **2026-10-16 NY 08:15 bearish CISD**, step one **closed** 15-minute candle at a time. Use offset `0` first and adjust to the matching event by **direction, confirmation time, start/confirm bars and price**, not by the newest number alone. Note **FVG THEN = none** and the **AT CLOSE** verdict. Advance to the later FVG candle: **LATER** may change, but **FVG THEN** and **AT CLOSE** must not.
4. Around **2026-10-08 bullish CISD linked to a live C2**, note **C2 THEN** when it first confirms. Advance beyond the later qualified C2 closure: the `LATER` field may fill while **C2 THEN** remains provisional.
5. Locate one CISD sharing a confirming candle with an aligned FVG. **THEN FVG born bar offset = 0**, with formation timestamp no later than CISD confirmation and immutable top/bottom after subsequent replay candles.
6. Record **MATCH** (not DRIFT or MISSING AUDIT) on at least three cases, including a non-eligible event; check the separate FVG-record-integrity row where an at-close FVG exists. **MATCH** is necessary for internal consistency but does not prove replay determinism.
7. Toggle the audit panel OFF and ON at the same replay endpoint, comparing raw CISD presence, Po3 phases, eligible/drawn counts, and overlays against the Phase B branch. Note that TradingView recomputes when changing inputs.
8. Check offset `0`, `1`, `19`, fewer than 20 events, a long replay with 100 retained events, and an empty-registry scenario. No out-of-bounds or table/object-limit errors should appear.

**Acceptance gate:** Do not merge into Phase B PR #5 or claim validated non-repainting behavior until Pine compilation and the three key replay invariants above are independently observed. This branch does not introduce alerts or execution.
