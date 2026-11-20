# Full Bandz Po3 with selectable CISD V2 (November 20, 2026)

## Purpose and status

This is the intended FULL Bandz indicator: retain its existing Po3, HTF, CRT-adjacent timing/reference, SMT/SSMT, PSP, T-Spot, FVG/VI, levels/opens, STDV, C1–C4, asset comparisons, header and all original settings. Substitute a validated V2 CISD into the chart-timeframe sequence pipeline while keeping a LEGACY switch.

- Branch: feature/full-bandz-cisd-v2-sequence-20261120
- New full source: indicators/Bandz_Po3_Full_V2_Integrated.pine
- Original frozen source remains unchanged: Bandz_Po3_Profiler.pine (experiment/cisd-v2-pine-logs-20261120)
- GitHub static integration regression suite: PASS.
- Native TradingView Pine v6 compilation of integrated file: **NOT YET TESTED**.
- Live alerting / 1/5/9 CRT integration: **NOT INCLUDED**.
- Experimental only; no claim of better trading outcomes.

This is NOT a clone of all proprietary Cephxs Po3+ functions. It restores and extends the full open Bandz functionality that already existed.

## New selection: Chart CISD engine

Under Settings → 4 · CISD + STDV:

| Engine | Chart-timeframe sequence CISD | Display |
|---|---|---|
| V2 (default) | V2 confirmed closed-bar signal feeds the same existing poLinkCisd slot 0 used by Bandz. It supplies event origin, level, confirmation bar to the original sequence and STDV logic | Sequence only: only C2-linked levels; All: all V2 confirmed levels, origin-anchored; All + C2 highlighted: V2 lines with thicker C2-linked ones |
| Legacy | The original Bandz raw CISD, C2-linking and all original legacy research outputs are unchanged | All existing Bandz legacy displays and advanced structural/audit labels |

Original V2 pivot/ATR/stretch/confirmation/invalidation algorithm was relocated **verbatim** to execute before the chart-CISD link step; it was NOT rewritten. All C1/C2/C3/C4, SMT/SSMT, PSP, FVG, T-Spot, status panel and STDV algorithms remain from Bandz. Confirmations are linked only on actual CLOSED bars; no retroactive/backdated sequences.

The original legacy detector is still present and running for archival diagnostics, but does NOT control sequence decisions when V2 is selected.

### What is not yet migrated to V2

- 3m and 5m CISD engines are still LEGACY for sub-3m/sub-5m charts when their sequence slot is selected. On a **15m chart**, select Sequence CISD from = Chart and V2 applies.
- All legacy forensic skip panels, C2 structural research event snapshots, audit counts and historical legacy event export remain available, explicitly associated with LEGACY. In V2 mode the legacy-only audit summary panels are suppressed rather than mislabelled as V2. Advanced V2 context labelling is not independently rebuilt.
- No new production alerts, backtest strategies, or CRT 1/5/9 trading filters are added. They are later development phases.

## TradingView Essential: two-minute installation

1. Keep your original Bandz Po3 indicator, research templates and layouts intact.
2. Open the full new Pine source via GitHub. Click Raw and copy all contents.
3. TradingView Pine Editor → New indicator → paste → Save as Bandz Po3 Full V2 → Add to chart.
4. If compilation fails, record the **first** Pine compiler error with line number. Do not hand-edit the detector logic.
5. Start on FOREXCOM:GBPUSD, 15m; set Chart CISD engine = V2; Sequence CISD from = Chart.
6. Detector settings: pivot left/right 1, bridge 2, scan 12, minimum run 1, expiry 10, ATR filter ON, minimum stretch/ATR14 0.5. These inputs are selected by default in this full V2 script.
7. Leave the normal Bandz quick toggles enabled for HTF candles, Po3, T-Spot, SMT/SSMT, PSP, FVG, levels and opens. They remain in the new script.
8. Start with CISD scope = All for visual examination of all confirmed V2 levels. Then choose Sequence only to see which become C2/Po3-linked.
9. Keep extra V2 diagnostic pending lines and event registry OFF initially. Only enable for research.
10. Save a new indicator template BANDZ - FULL PO3 - CISD V2 - 15M, and a separate chart layout. The existing saved indicator template does not automatically transfer between differently named scripts.

## Two previously independently validated V2 signals

On FOREXCOM:GBPUSD 15m, **candle CLOSE UTC**:
- 2026-11-17 07:45 BEAR, reference level 1.31911
- 2026-11-18 07:30 BEAR, reference level 1.31889

TradingView candle time axis generally labels the candle OPEN 15m earlier. Select All to confirm both references; Sequence only hides unlinked CISDs by design.

## Acceptance boundary

1. Native TV compilation.
2. Visible HTF candles, Po3 C1/C2 profile, SMT/PSP, FVG and levels/opens still work.
3. All mode shows known V2 CISD references beginning at opposing-run first candle; they are not claimed to be knowable until the confirming close.
4. Sequence only mode links V2 to C2 in eligible examples and STDV uses the chosen new reference.
5. Switch back to Legacy; original Bandz raw CISD and sequence behavior returns.
6. No new alerts until this integration is accepted.

Don't reopen the 17-event historical parity loop for a drawing/connection defect. Historical V2/archived-Cephxs agreement (17/17 V2-confirmed events in bounded in-sample period, one extra same-level Cephxs repeat) is a detector-only result. It is not a test of whether C2 integrations, T-Spots or alerts are correct; validate those separately and minimally.
