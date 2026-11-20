# Bandz Po3 V2 — clean Visual Test (November 20, 2026)

Purpose: give the trader a full-feature Bandz Po3 indicator with the integrated closed-bar CISD V2 engine, while reducing research-only settings during several weeks of personal visual observation.

## Files / preservation

- VISUAL-TEST: indicators/Bandz_Po3_V2_Visual_Test.pine
- FULL-INTEGRATION REFERENCE (untouched): indicators/Bandz_Po3_Full_V2_Integrated.pine
- ORIGINAL RESEARCH BASELINE (untouched): Bandz_Po3_Profiler.pine
- Draft full-profile PR #21 and Phase 2 research source remain available. This build does not replace them.

## What is retained in the interface

- All normal Bandz Po3 controls, comparison assets, HTF candles, Po3 C1-C4, T-Spot, SMT/SSMT, PSP, Entry FVG, FVG/VI, HTF levels / opens, STDV, labels and styling.
- Chart CISD engine selector (V2 default, or Legacy), CISD display scope, colors, Sequence CISD from Chart / 3m / 5m, original Legacy sensitivity / run / invalidation settings.
- Historical CISD line count and whether to show invalidated CISDs (faded).
- V2 engine inputs (pivot confirmation left/right, opposing stretch search, max stretch, minimum run, expiry, ATR filter / threshold). All originally configured defaults are preserved.

## What is removed from the settings panel

50 research-only controls, including: legacy structural filters, research labels, killzone display diagnostics, research FVG lifecycle zones, event-time audit, later-outcome audit, legacy skip forensic snapshot, V2-vs-Legacy disagreement table, CSV/Data Window opt-in, and Pine Logs event output. The latter research functions remain in the preserved source file.

Importantly, the visual-test build also **retains the full internal detection code** and most legacy research code as fixed-default, disabled settings, rather than deleting portions of the original engine. This makes it easier to compare against the research baseline and prevents accidental changes to the Po3 logic. It is a UI cleanup, not performance refactoring or trading-rule optimization.

## Installation / first-use check

1. Keep the already working full-profile V2 script and saved chart layout. Do not overwrite it.
2. Open the GitHub visual-test .pine file and use Raw → Copy.
3. TradingView Pine Editor → New indicator → paste and Save as Bandz Po3 V2 Visual Test → Add to chart.
4. Check all familiar Bandz controls are available; the new settings order includes the concise '4A · CISD V2 detector' section without any audit or logging groups.
5. On FOREXCOM:GBPUSD M15, select Chart CISD engine = V2, Sequence CISD from = Chart, CISD scope = All initially. Confirm expected source-anchored lines and unchanged HTF/Po3/FVG/SMT appearance.
6. Return CISD scope to Sequence only for normal Po3 C2-linked chart use. If you want all CISDs visible, leave All enabled.
7. Save a new TradingView indicator template for this build. Do not assume TradingView automatically transfers every input from the old separate script.

## Validation and limitations

- GitHub static regression test PASS: unchanged computational source from the original STDV configuration onward (includes the full frozen V2 detection engine, legacy engine linkage, all Po3/SMT render logic), and 50 fewer input controls.
- There is no native Pine compiler or live TradingView replay in GitHub Actions. Native compilation and visual acceptance of this exact visual-test script must be confirmed in TradingView.
- This research stage is NOT an approved trade-entry signal, statistical advantage, automated alert service or fully Cephxs-equivalent indicator.
- Any tuning of V2 detector inputs changes detections. For apples-to-apples comparisons, keep 1 / 2 / 12 / 1 / 10 and the ATR gate ON at 0.5, and note any exceptions in observations.

## Future development

Retain research functionality on the full-profile source and branch, restore investigative controls there when useful, and use this visual-test file as the observation baseline. Alerting and 1/5/9 CRT integration remain the next separate project phases.
