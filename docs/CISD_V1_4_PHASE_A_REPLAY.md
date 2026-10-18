# CISD v1.4 Phase A — TradingView replay acceptance

**Branch:** `feature/cisd-v1.4-structural-qualification`

**Status:** Research implementation awaiting Pine v6 compilation and replay validation. No changes to trade entries, alerts, legacy `All` / `Sequence only` detections, or Po3 C1/C2 model. The design contract is in `CISD_V1_4_DESIGN.md`.

## Chart and inputs

Use EURUSD 15M → 4H, symbol/feed matched to prior validation, timezone **America/New_York**. Disable Auto HTF and Auto Count; use HTF1=1H (8), HTF2=4H (6), HTF3=1D (5), Profile on HTF2, sequence Auto. Use the same previous Standard sensitivity and Min run 1 as the v1.3 test; do **not** infer quality from the settings.

- CISD: **All + C2 highlighted**
- Research: retain events 100; draw events 30
- Research: draw filter **All**
- Research: faded invalidated CISDs **On**
- Research: diagnostic labels **On**
- Research: label verbosity **Full**
- Research: label events **C2-linked only** for first replay; use **All** to inspect unlinked references
- Research: max labels **10**
- Research: include FVG/C2 context in Full labels **On** (optional v1.3 context)
- **NEW: Research: structural metrics in Full labels On**
- FVG lifecycle zones/labels **Off** to keep chart uncluttered. FVG *event history* still runs in this research CISD mode.
- Retain FVGs 80, FVG bars before CISD 2, after 4

## Fields

- **C2 at CISD: unlinked | provisional at CISD | confirmed at CISD.** A provisional C2 can later close, but this field is **never upgraded retrospectively**.
- **Sweep: yes/no/n/a.** A C1 extreme sweep on the selected Bandz linked C2, not an independent liquidity or swing sweep. `n/a` means unlinked.
- **C2 closed (observed)** is the v1.3 timestamp for *eventually* qualified C2. A timestamp appearing later is research outcome, **not an early signal**.
- **Body/range** = 100 × abs(C−O)/(H−L). Zero-range → n/a.
- **Body/ATR14** = abs(C−O)/ATR(14), chart timeframe. ATR unavailable → n/a.
- **Close strength** = 100 × (C−L)/(H−L) for bull; 100 × (H−C)/(H−L) for bear. High values denote closes nearer the directional extreme; they are descriptive, not a trading score.
- **Aligned FVG at CISD**: nearest independently confirmed same-direction FVG within the preceding 2 chart bars, **inclusive of an FVG born at the CISD candle close**; must not have already invalidated at the event's close. May read `0 bars`.
- **After**: a separately time-stamped FVG formed **strictly after** the CISD candle and within the next 4 bars. It is hindsight context and must say **(later)**.

## Required tests

1. **Compile first.** Check Pine Editor errors and TradingView runtime (incl. when `Research: structural metrics` is disabled).
2. **EURUSD 8 October, 15M → 4H:** Capture the first bullish CISD during live C2; its Full label must show `provisional at CISD`. Advance until C3, verify eventual `C2 closed (observed)` timestamp appears while the **same earlier** `C2 at CISD` text remains unchanged. Do not treat C2 eventual validation as a retroactive confirmation.
3. **EURUSD 14 October:** Compare a bearish CISD at formation and after the subsequent FVG/reclaim. The **at CISD** FVG field cannot gain a later FVG. Only **After** may change to `+N bars (later)`. Metric percentages remain invariant. FVG and CISD can invalidate independently.
4. **GBPUSD 8 October:** Confirm the raw, live-C2 and xC2 cases show independent snapshot statuses, with no unintended changes to prior C1/C2 drawings.
5. **Legacy parity:** Change CISD to `Sequence only` then `All` and compare against merged `main` on same feed/settings/bar. Metrics must not appear or alter baseline structures/levels/timing.
6. **Disable the new checkbox** and confirm all v1.3 research lines/drawings remain unchanged.
7. **Performance:** Step through a longer 15M replay; no object limits or runtime exceptions.

## Failure reporting

If Pine cannot compile, provide the **exact line and error** before any other screenshot. If it compiles, return one **close-up of a Full CISD label** during live C2, and one after C2 closes. If an earlier field mutates, record candle time and replay endpoint; this is a regression.

## Boundaries

Do not enable new execution, alerting or trade filters. Phase B will add **optional** diagnostic selection only after this snapshot behavior is proven. No claim of Cephxs algorithmic parity is made from these observations.
