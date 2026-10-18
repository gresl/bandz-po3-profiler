# CISD v1.4 — Phase C: event-to-outcome research contract

**Status:** Phase C kickoff / evaluation protocol. **Parent baseline:** `feature/cisd-v1.4-event-time-audit` (Phase A + B + event-time audit). **Data:** not yet collected. **Objective:** evaluate whether *contemporaneous* structural qualifiers make a useful difference; not to mimic private indicator internals or retrospectively optimize a trade strategy.

## 1. Frozen event identity and comparison cohort

Collect **30–50 consecutive raw confirmed CISD events**, not 30–50 attractive chart examples, in prespecified windows. Record rejected/no-trade setups. Use a fixed TradingView feed and configuration for each cohort, with EURUSD 15m -> 4h as primary and GBPUSD 15m -> 4h as a separate replication cohort if history is available. The Oct 8 and Oct 16 screenshots are **regression fixtures**, not evidence of predictive edge.

Unique-in-this-study event identity: feed (`syminfo.tickerid`), chart timeframe, Po3 profile/anchor timeframe, New York confirmation-close timestamp, direction, confirmBar and level. Bar indices are local to the loaded history and must NOT serve as cross-feed global keys. Record script commit SHA, settings profile and chart timezone; never compare endpoints after changing settings as though the computation were unchanged.

At confirmation freeze these inputs: raw signal side, CISD level, C2-linked, C1-swept-at-confirm, C2-already-closed-at-confirm, body/range %, body/ATR14, directional-close %, aligned FVG known-at-confirm, baseline draw filter, killzone label, and the combined eligible verdict. If FVG born time is missing despite an at-close pointer, flag `missing_evidence`; do not silently count it as pass.

Keep a parallel **manual model assessment made with future bars hidden**: `valid`, `invalid`, `uncertain` and a short reason code/comment. An outcome (later directional price movement) cannot substitute for this technical validity label. Preserve `uncertain` cases.

## 2. Objective forward observations, not trade P&L

Use the **CISD confirmation candle close** as the reference price, and ATR(14) frozen at that close as a volatility normalizer. This is an *analytical reference*, not an assumed filled order. Consider **16** and **32** subsequent completed 15-minute bars (4h and 8h). Both horizons are prespecified. Do not peek beyond the current closed Replay bar; incomplete horizons remain `censored`.

For bullish signals:
- Favorable excursion = (maximum subsequent high - confirmation close) / ATR_at_confirmation.
- Adverse excursion = (confirmation close - minimum subsequent low) / ATR_at_confirmation.

For bearish signals reverse price direction:
- Favorable excursion = (confirmation close - minimum subsequent low) / ATR_at_confirmation.
- Adverse excursion = (maximum subsequent high - confirmation close) / ATR_at_confirmation.

Start at the **first bar after** CISD confirmation; exclude the confirming candle's wick. Record MFE, MAE, terminal close-to-reference return (ATR units), and the first later bar at which +1 ATR and -1 ATR are touched. If both thresholds are touched within one OHLC bar, order is **unknown**; label `ambiguous`, never manufacture a first-hit win. Handle `na`/zero ATR explicitly as `not_evaluable`.

Outcome metrics are appended in a separate *LATER* namespace. They must **never** feed event-time filters, move CISD timestamps/levels, or relabel the earlier `AT CLOSE` decision. Do not compute from future data via an unguarded `request.security` or lookahead mode.

## 3. Compare condition classes, without curve fitting

Measure cohorts for raw CISDs, any live C2 association, C1 sweep at CISD, C2 confirmed *at* CISD, displacement pass, aligned FVG known *at* CISD, and the enabled-filter intersection. The documented 55% body/range / 0.6x body/ATR / 70% close thresholds are **research hypotheses**, not tuned values. Include all event-time rejects in denominators.

At 30–50 cases report:
- N raw and class membership; share excluded by each gate and by the combined AND predicate.
- Agreement with blinded manual `valid/invalid/uncertain` labels; valid setups lost by each gate and invalid setups removed by each gate. Keep `uncertain` separate.
- At each fixed horizon, descriptive distributions of favorable/adverse excursions and terminal return. Show denominators and censored events.
- +1/-1 ATR first-hit counts including ambiguous same-bar order, no-hit and censored events.
- Session, symbol and date stratification; identify correlated events on the same day. Small samples warrant descriptive interpretation, not significance or profitability claims.

**Do not optimize thresholds on the evaluation sample.** If refinements are indicated, document them as new hypotheses and require an independent out-of-sample period before recommending default changes. Observed Cephxs and Bandz marker agreement should be compared on identical feed/timeframe/candle-close data and by marker category, not assumed equivalent merely from similar shapes.

## 4. Proposed implementation slices (isolated, reviewable)

**C1 — Baseline and schema:** preserve the Phase B frozen snapshot; define a row-based capture format and mandatory null/unknown states. No Pine algorithm edits required for this slice.

**C2 — Optional forward research instrumentation:** only in `All + C2 highlighted` research mode, track the future *closed-bar* OHLC envelope and 16/32-bar observations for retained raw events. Store reference close and ATR *at confirmation* separately. A post-close label or panel may display outcomes; defaults OFF. Keep raw CISD, C1/C2, FVG detection, structural filtering and legacy plots untouched. No alerts or external execution.

**C3 — Sample capture and labeling:** fill the study manifest from consecutive events using the existing event audit and any C2 outcome instrumentation. Mark each as technically valid/invalid/uncertain **before** revealing forward outcomes, or annotate an explicit `review_not_blinded` limitation where that cannot be done. Evaluate only completed horizons.

**C4 — Fixed analysis and decision:** create a reproducible summary, note rejected-good and passed-bad cases, compare against Cephxs screenshots where available and decide whether tighter detection or an independent PB detector is justified. No rule/threshold changes without separate approval.

## 5. Acceptance / regression gates

1. Pine v6 compiles and the optional Phase C instrumentation OFF matches the Phase B audit branch in raw event count, confirmations, C1–C4 drawings, FVG history, legacy modes and Phase B counts at identical Replay endpoints.
2. Phase C outcomes are empty immediately at confirmation, accumulate **only after** the subsequent chart candles close, finalize at 16/32 bars, and never alter frozen `THEN` or `AT CLOSE` data. All reference values stay constant under Replay.
3. 2026-10-08 provisional C2 and 2026-10-16 later-FVG fixtures preserve their prior classification and `MATCH` status. Count panel and audit offset behavior remain stable.
4. Replay across zero, few and 100 retained events without out-of-bounds, object-limit or timeout exceptions; include GBPUSD/xC2 before merge.
5. Mark missing/partial history and ambiguous OHLC threshold hits explicitly. No execution, new alert/webhook behavior or claims of model profitability.

## 6. Capture manifest

Use `research/cisd_phase_c_sample.csv`. It deliberately starts with **headers only**, not invented cases. Never enter future observations in at-close columns. Raw/manual labels and outcome columns are logically independent.

**First development deliverable:** the closeout + this protocol + empty manifest. It introduces **zero Pine risk** and provides an agreed metric contract before adding optional event-outcome code.

## 7. Phase C C2 code status (first optional implementation)

**Implemented on this Phase C branch; NOT yet Pine-compiled or TradingView-replayed.** Commit `9787d74` adds:

- `Research: later 16/32-bar outcomes` (default **OFF**), only in `All + C2 highlighted` research mode.
- Immutable confirmation-close and ATR14 references on the retained event; no change to raw CISD triggers, Phase B eligibility, existing C2/FVG linking or legacy renderers.
- Post-event **closed-bar** accumulation for bars +1 through +16 and +32, including max high/min low, horizon terminal close and first 1-ATR directional/adverse touches.
- Six optional rows in the existing event-time audit panel (enable **both** `Research: event-time audit panel` and `Research: later 16/32-bar outcomes`). These rows show selected event offset's reference, number of closed bars observed, MFE/MAE, terminal return and first-hit ordering. `PARTIAL`/ `FINAL` and `AMBIGUOUS same bar` are deliberate states.

**First acceptance session (user action):** Compile the complete `Bandz_Po3_Profiler.pine` from this branch in TradingView Pine v6, EURUSD 15m->4h. With both switches OFF verify existing drawings. Then enable audit + outcomes at an event's confirmation candle close: `closed bars observed = 0`, forward MFE/MAE n/a. Advance one **completed** 15m candle: `closed bars observed = 1`, only LATER rows may move; frozen THEN/AT CLOSE and MATCH must not. After +16 bars, 16-bar terminal and hit status must say FINAL; after +32 bars, the 32-bar status must also finalize. Check the same selected event with audit offsets 0 and 1 while the newer event comes in. A both-sides 1-ATR touch within one candle must be labeled AMBIGUOUS, not a favorable win. Confirm no Pine runtime/object-limit error.

**Important limitations:** the study manifest is not auto-exported by this initial UI slice; rows require review/capture. The chart screenshots and user compilation will be the first runtime validation. The first-hit result uses OHLC high/low, so intrabar order remains unknown in ties. Counts are for retained events, not a universal population. No claims of TradingView runtime validation before the operator's report.
