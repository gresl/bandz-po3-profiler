# CISD v1.4 Phase B — Structural display filters (research)

**Branch:** `feature/cisd-v1.4-phase-b-display-filters` (stacked on Phase A, draft PR #4).  
**Scope:** Research renderer only. **Not a new CISD algorithm, order-flow confirmation, trade signal, alert, strategy, or profitability claim.**  
**Baseline:** `main` remains at merged v1.3; Phase A fields are snapshotted on the closed CISD chart candle.

## Inputs and exact logic

Use **CISD = All + C2 highlighted** to activate the research event registry/renderer. `Sequence only` and `All` remain unchanged. The existing **Research: draw filter** (All / C2-associated / Killzones / C2-associated + Killzones) is still applied first, then Phase B requirements are ANDed onto it.

All new Phase B filters default **OFF**:

| Input | Default | Qualification |
|---|---|---|
| **Structural: C2 requirement** | Off | Optional `C1 swept at CISD`: `ev.c2SweepAtConfirm`, or `C2 already confirmed at CISD`: `ev.c2QualifiedAtConfirm`. Both are **snapshots** at the CISD candle close. |
| **Structural: require displacement** | Off | Requires all three pre-recorded measurements to meet user thresholds. `na` fails when required. |
| **Min body/range %** | 55% | 100 × abs(C−O)/(H−L); denominator zero → `na`. |
| **Min body/ATR14** | 0.6x | abs(C−O)/chart-TF ATR(14). ATR unavailable or zero → `na`. |
| **Min directional close %** | 70% | Bull: 100 × (C−L)/(H−L); bear: 100 × (H−C)/(H−L). |
| **Structural: require aligned FVG known at CISD** | Off | Requires `alignedFvgAtConfirmBar` from v1.4 Phase A, not the later FVG reference. FVG must have confirmed on/before CISD close and not been previously invalidated. |
| **Structural: show filter counts** | Off | Bottom-left optional table counting retained history and eligibility before/after draw cap. |

These thresholds are **illustrative hypotheses**, not backtested optima. Start with only one new requirement at a time to measure what disappears.

**Excluded from qualification:** `c2ClosedAt` when it is later than the CISD candle; `alignedFvgLaterBar`; whether the CISD eventually invalidates; forward performance; later xC2 outcomes. A post-confirmation event can change the diagnostic label but **never a frozen structural eligibility flag**.

## Summary table semantics

Counts span only **retained** `poCisdEvents` (configured 10–250, often 100), not every historical event since chart inception. Rows:

- **C2 linked:** initial Bandz chart-CISD association to live C2.
- **C1 swept at CISD:** matched HTF C2 had already exceeded C1 extreme.
- **C2 closed at CISD:** C2 was already valid/closed at the CISD confirmation.
- **Displacement passing:** all three numeric thresholds pass, regardless of whether the displacement switch is enabled.
- **Aligned FVG known:** Phase A at-confirmation aligned FVG exists; not subsequent FVGs.
- **Eligible (combined):** legacy context filter AND Phase B requirements AND recency (within 4800 bars) AND optional invalidated-CISD visibility.
- **Drawn (cap):** minimum of eligible and the configured Research: draw events maximum.

Because individual category counts are **not independent**, do not add them together. If a filter is disabled, its category count is still shown descriptively.

## Expected non-lookahead behavior

**October 8 EURUSD**: A bullish C2-linked CISD may be provisional at its confirmation, with `C1 swept at CISD = true`. It may pass the sweep filter while **failing** the `C2 already confirmed at CISD` filter. Advancing to C3 must not make that same CISD suddenly appear under the latter filter. Its later C2 close can be displayed as *retrospective diagnostics only*.

**October 16 EURUSD, bearish ~08:15 New York**: If the same-direction FVG is `none` **at** the CISD confirmation and appears `+1 bar (later)`, that CISD must **not** qualify under `require aligned FVG known at CISD` either before **or after** that later FVG forms. A separate same-candle (`0 bars`) bullish FVG at ~10:00 may qualify at its own confirmation close if not invalidated.

**October 8 GBPUSD**: Show the existing C2-live and xC2 visual sequence, verifying no change to C1/C2 selection when any filter is toggled.

## TradingView acceptance plan

1. **Compile first**, run on EURUSD 15M → 4H, `America/New_York`, Auto HTF/Auto count OFF, HTF1=1H/8, HTF2=4H/6, HTF3=1D/5, profile source HTF2. Use the same Bandz v1.4 Phase A CISD/label settings and `Research: draw filter = All`.
2. **No-filter parity:** Leave all three structural filters OFF and `Structural: show filter counts = OFF`. Drawings should match Phase A exactly on the same Replay endpoint. `Sequence only` and `All` remain unchanged.
3. **Counts:** Turn on `Structural: show filter counts`. Counts must not change when only this table is toggled. `Eligible` may be smaller than retained due to recency, legacy context and invalidated-event visibility. `Drawn` must equal min(Eligible, research drawing cap).
4. **C2 sweep only:** Set C2 requirement to `C1 swept at CISD`. On live C2, the qualifying CISD should remain shown, with fewer unlinked raws. Compare table `Eligible` to baseline.
5. **Confirmed at CISD:** Select `C2 already confirmed at CISD`. Most earlier live-C2 CISDs may disappear, **even when C2 later closes**. This is correct, not a bug. Confirm by advancing replay. If none meet the criterion, table can show zero.
6. **Displacement only:** Return C2 mode Off. Enable displacement; try initial 55%/0.6x/70%. Observe reduced eligible count. Change each threshold by small increments and ensure raw CISD origins/levels remain stable. Check missing ATR yields nonqualification, not a crash.
7. **Known FVG only:** Disable displacement, enable `require aligned FVG known at CISD`. For the October 16 bearish CISD, confirm no retroactive appearance following the later FVG. A zero-offset already confirmed aligned FVG may qualify.
8. **Combine:** Enable `C1 swept at CISD` + displacement + FVG. AND semantics, so eligible must be <= each filter alone on the same historical endpoint.
9. **Regression:** Compare EURUSD and GBPUSD (and preferably one longer history), checking `Sequence only`/`All` parity, C2 projection, FVG lifecycle toggle, and no runtime/drawing-limit problems.

**Proof requested after successful compile:** One screenshot with research mode All, filter table ON, no structural requirements; one with C2 sweep + displacement ON; and one with known-FVG filter ON during the Oct 16 bearish CISD sequence. Capture the same Replay endpoint for valid count comparisons. Do not compare different replay endpoints as if they were identical samples.

## Limits and next steps

No alert or order-execution changes. **Phase C** will compare these transparent context classes to a labeled 30–50-event sample (using bar-close-aligned, timestamped ground truth), report missed valid CISDs and excluded invalid setups, and only then consider whether quality filtering improves discretionary review. Propulsion Block identification remains a separate subsequent module, not a synonym for FVG or CISD.
