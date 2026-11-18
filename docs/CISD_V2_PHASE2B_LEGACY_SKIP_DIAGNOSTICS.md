# Phase 2B — Legacy CISD Skip Diagnostics (no detector changes)

**Branch:** `experiment/cisd-v2-legacy-skip-diagnostics-20261118`  
**Parent:** `experiment/cisd-v2-disagreement-audit-20261117`  
**Status:** Pine v6 compilation in TradingView and Replay parity **pending**. Python synthetic gate tests are not Pine execution tests.

## Question

Why does legacy Bandz omit the `FOREXCOM:GBPUSD`, 15m, **2026-11-12 02:30 UTC** bearish close at approximately **1.32745** when pivot-based Bandz V2 and Cephxs independently display the bearish CISD on the same completed candle?

The current evidence is in [the V2-only case fixture](../research/fixtures/GBPUSD_FOREXCOM_20261112_0230Z_V2_ONLY.md). Cephxs first visibly draws the solid line after the 02:15–02:30 UTC candle closes, not proof of the first realtime intrabar tick. This is a **mechanical** reference case, not a validated trading setup.

## New 4D · Legacy CISD skip diagnostics

New settings, OFF by default:

| Input | Initial value |
|---|---|
| Skip audit: capture one legacy close | OFF (turn ON only for audit) |
| Skip audit: target close NY | `2026-11-11 21:30` |
| Skip audit: target side | `Bearish` |
| Skip audit: show snapshot (middle left) | ON (effective only when audit enabled) |

2026-11-11 21:30 **America/New_York** corresponds to **2026-11-12 02:30 UTC** (EST, UTC−5). The field selects the **closing** time, not the opening bar time. Input is independent of the old fixed event audit selector (which can remain set to the earlier bullish `2026-11-12 02:30` NY / 07:30 UTC).

The snapshot freezes on `barstate.isconfirmed` and is taken inside the **actual legacy production code path**, after the run state has been updated for the targeted candle but **before** trigger/reset clears the run variables. It captures:

- selected side and timestamp (UTC / NY)
- chart open/close prices and actual feed/timeframe
- prior opposing-run length, start bar/age, first/last candle opens
- Standard/Sensitive reference level and configured minimum-run threshold
- gate booleans: correct candle color, level available, run length, close through level, run age <=60, duplicate-event guard
- actual legacy `poCisdNewBull` or `poCisdNewBear` production flag **after** evaluation
- a single **first failed predicate** diagnosis, with all gate results shown for transparency
- any matching V2 retained confirmed event at exactly the same closing timestamp, with pivot/born-bar metadata; this may be unavailable if V2 history is truncated

**No raw CISD predicate, V2 pivot logic, alert, Po3 sequence link, drawing, or quality filter has been changed.** This is a forensic measurement patch only. Do not mistake a `NO_CLOSE_THROUGH` / `MIN_RUN` diagnosis for proof that relaxing the associated filter is beneficial.

## TradingView acceptance — single 02:30 event

1. Keep your prior ATR0.5 and disagreement layouts untouched.
2. Copy the `Bandz_Po3_Profiler.pine` source **from this branch**, paste into a **new TradingView Pine Editor copy**, Save → Add to chart. Report exact compiler errors if any.
3. `FOREXCOM:GBPUSD`, **15m**, standard candlesticks; do not change source feed, chart symbol or time zones mid-test.
4. Under **4C**, use `V2 detector ON; pivot=1; bridge=2; additional scan=12; min opposing run=1; expiry=10; ATR stretch gate ON; min stretch / ATR14=0.5`. The existing `V2 audit: compare legacy vs V2` can remain ON or be hidden to reduce clutter.
5. Under **4D**, turn ON the skip audit. Target **Bearish** / **2026-11-11 21:30 NY**. Do not change legacy Standard/min run 2.
6. Bar Replay: start before the Nov 12 **02:15–02:30 UTC** candle, advance until the **02:30 close is processed** (e.g. endpoint at 02:45 UTC). Allow chart to load enough historical bars.
7. Screenshot only the **middle-left skip snapshot panel**, with preferably the top-left V2 event registry visible. Record `First failed predicate`, `Opposing run len/age`, `Selected level` and `Actual legacy event`. No extra chart screenshots needed.

### Expected verification (not prejudged outcome)

- The snapshot should capture an actual 02:30 UTC historical closed-bar decision. `NOT CAPTURED` indicates wrong NY time, missing loaded history, endpoint before close, or disabled audit.
- If `MIN_RUN` fails with `run len=1`, the short opposing-run hypothesis is supported for the legacy skip. It does **not** mean we should globally change `poCisdMinRun` to 1.
- If `NO_CLOSE_THROUGH` fails, inspect legacy Standard's reference level vs V2's pivot-origin level before designing changes.
- If a different gate fails, address that exact condition before altering the V2 engine.
- If all gates pass but the production flag says NOT CONFIRMED, treat this as an **instrumentation / lifecycle defect** and investigate; do not tune thresholds.

### How this advances detection quality

The next step is **cause-specific and test-driven**:

1. Establish the actual failed legacy predicate on the accepted V2/Cephxs positive case.
2. Collect one **negative control** that V2 marked but Cephxs did not; avoid circularly defining quality as matching Cephxs.
3. Propose a narrowly gated change to an independent V2 variant, or improve pivot candidate validity, keeping legacy untouched and unmergeable until tested.
4. Evaluate exact same-feed closed-event timestamps and structures across multiple bullish/bearish cases; later measure false positives / delayed detection / invalidation *without* future data leakage.
5. Never assume a line anchored to an earlier candle was confirmed early. TradingView's indicator execution model can show unconfirmed realtime closes.

## Offline regression

`python3 -m unittest discover -s research/tests -v`

`research/cisd_legacy_skip_oracle.py` contains a pure reference decision ordering model; `research/tests/test_legacy_skip_oracle.py` tests bearish/bullish gates, min-run failure, missing level, close-through, age and duplicates. Test success proves the Python reference decisions only.

## Interpretation / merge policy

Keep this branch and its draft PR separate from Phase 2 and main. Merge only after Pine compile, a correctly captured 02:30 target panel, and source-level inspection of the actual failed gate. Indicator accuracy and trade profitability are **not proven**.
