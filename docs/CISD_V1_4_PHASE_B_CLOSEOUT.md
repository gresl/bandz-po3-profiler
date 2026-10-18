# CISD v1.4 Phase B — replay research closeout (2026-10-18)

**Research validation status:** CLOSED for the agreed EURUSD event-time audit cases, by user approval. **Code/merge status:** NOT MERGED; the stacked draft PRs remain under review. This is a scoped validation result, not a certificate of universal non-repainting or predictive efficacy.

## Baseline and dependency chain

- `main`: merged Bandz v1.3 baseline.
- PR #4: `feature/cisd-v1.4-structural-qualification` -> `main` (Phase A, draft).
- PR #5: `feature/cisd-v1.4-phase-b-display-filters` -> Phase A (Phase B display filters, draft).
- `feature/cisd-v1.4-event-time-audit`: builds on Phase B and adds optional audit panel (Pine v6 compiled in TradingView).
- Phase C work branches **from this audit baseline**, not from `main`. No upstream draft branch is merged by this closeout.

## Evidence observed in TradingView Bar Replay

- **EURUSD, 15m chart / 4h Po3, New York chart time, 2026-10-08:** A bullish CISD linked to a live C2 remained provisional **THEN**, even after a later qualifying C2 closure appeared in the **LATER** section. Audit offset and closed-bar Replay comparisons did not retroactively promote the original decision.
- **EURUSD, 2026-10-16, bearish CISD around 08:15 NY:** Aligned same-direction FVG **THEN** remained absent where the FVG was first observed **+1 bar later**. Later FVG/invalidations did not change the original classification.
- **EURUSD, 2026-10-16, bullish 06:15 and 10:00 examples:** Selected-event panels kept `THEN` measurements/flags and `AT CLOSE` eligibility fixed while replay advanced. `LATER` observations were allowed to change. The audit panel showed `MATCH` on the examples provided.
- **Compile:** user compiled the event-time-audit Pine source successfully in TradingView.

These checks support the **as-known-at-confirmation vs later-observed** distinction and internal predicate consistency on the chosen replay cases. `MATCH` alone would not establish independent replay determinism.

## Research baseline to preserve

1. Do not alter raw `poCisdNewBull`/`poCisdNewBear`, Po3 C1–C4 state machine, linked C2 logic or legacy `All`/`Sequence only` visualizations.
2. Audit/qualification uses only frozen at-confirmation fields; no later C2 closure, aligned FVG, price outcome, or invalidation can upgrade the historical at-close decision.
3. Phase B structural requirements are opt-in research drawing filters (OFF by default); no trade entries, alerts or execution.
4. Freeze source branch and documented replay fixtures before changing Phase C evaluation logic.

## Coverage not established by these screenshots

These were focused replay observations, **not** a complete release/merge gate. The following remain separately testable before merging or calling the code production-ready: GBPUSD/xC2 and legacy mode regression; offset 19, empty/short history and 100-event cap; combined-filter monotonicity at identical endpoints; full performance/object-limit runs on long histories; cross-feed/timezone behavior; independent comparison against Cephxs. Do not infer a profitable edge.

## Transition

Phase C is **event-to-outcome research** on a prospectively defined set of 30–50 raw CISDs, including rejected signals and no-trade conditions. See `CISD_V1_4_PHASE_C_RESEARCH.md`. Propulsion Blocks and strict/latest-run alternate CISD detection remain subsequent, independent efforts.
