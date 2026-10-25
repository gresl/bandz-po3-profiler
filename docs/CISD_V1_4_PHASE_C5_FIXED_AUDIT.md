# Phase C5 — fixed-event CISD audit selection (research UI only)

**Branch:** `feature/cisd-v1.4-phase-c-fixed-event-audit`; stacked on draft C4 PR #8. Changes only the audit panel selection and adds two inputs; the raw CISD engine, Phase B gates, C1/C2, FVG, alerts, drawings, and Phase C outcome calculations are unchanged.

## Why
The previous `Research: audit newest-event offset` was a **relative selector**, not an event key. Offset zero follows each new confirmed CISD. Observed Oct 16 replay "counter resets" were switches to newer events; the original event remained in retained history and reached 32/32 when found again.

This behavior is **not evidence of historical CISD repainting**, nor does this UI fix establish that every underlying signal is non-repainting.

## Controls
- `Research: audit selection mode = Newest offset` (**default**): original 0/1/2 newest-first browsing. Old offset behavior is preserved.
- `Research: audit selection mode = Fixed NY close`: ignores offset and selects by **CISD confirmation-close** wall-clock date/time in `America/New_York`, using `Research: fixed CISD close NY` format `YYYY-MM-DD HH:mm`.
- Example target: `2026-10-16 10:00` (do not enter candle open time). Use the event timestamp shown by the audit panel rather than guessing from the chart x-axis.
- A missing or blank target, an event no longer retained, or multiple events in the same NY minute produces an explicit warning; **there is no silent fallback to another CISD**.
- An NY local timestamp could be duplicated near DST fall-back. In that case, use relative mode to inspect both or defer the case rather than arbitrarily selecting one; the fixed selector intentionally warns on ambiguity.
- The fixed key is scoped to the current chart symbol, timeframe, and loaded event array. Changing the chart feed, timeframe, study inputs, Replay history, or loaded bars may alter the event population. Only collect reproducible observations on an unchanged, recorded configuration.

## TradingView compile and Replay acceptance (operator required)
1. Compile the full Pine v6 script from this branch, `Bandz_Po3_Profiler.pine`. Note compiler messages and exact script revision.
2. Keep the prior EURUSD `FOREXCOM:EURUSD` 15m -> 4h research configuration: `CISD = All + C2 highlighted`; audit panel ON; later 16/32-bar outcomes ON. Keep displacement and FVG experiment settings exactly as in the saved template.
3. With `Newest offset`, verify unchanged appearance and audit event switching as new CISDs confirm (baseline).
4. Set `Fixed NY close` and `2026-10-16 10:00`. Before the event is available, the panel must report `NOT FOUND` or `No retained events yet` (depending on Replay); it must not show another event's details.
5. At the target confirmation, verify `BULL 2026-10-16 10:00` at the same CISD level as the prior audit. The outcome count starts at 0/32; after the **next completed** 15m bar it reaches 1/32.
6. Move through later CISDs without modifying indicator settings. The panel must continue showing the target BULL event, with increasing count, unchanged frozen confirmation evidence and `MATCH`, until 16/32 and 32/32. Later FVG and invalidation observations may evolve normally; they are not at-close inputs.
7. Enter a nonexistent time such as `2026-10-16 10:01` and confirm a visible `NOT FOUND` warning **without stale outcome rows**. Empty target must request a timestamp. Revert to `Newest offset` to confirm fallback behavior only when explicitly chosen.
8. Repeat one fixed-event check for Oct 8 and a bearish example. Also check no exceptions when zero events or when the selected event falls outside retention.

**Not completed by this commit:** TradingView Pine compilation and runtime Replay verification. Do not infer correctness from a successful GitHub commit. This is a draft research tool, not an entry signal or trading recommendation.
