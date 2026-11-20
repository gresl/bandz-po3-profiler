# Phase 2D — Essential-compatible historical CISD logs

**Branch:** `experiment/cisd-v2-pine-logs-20261120`  
**Parent:** `experiment/cisd-v2-batch-export-20261119`  
**Status:** **ACCEPTED on TradingView Essential 2026-11-20**: Pine v6 compiled, native `Date,Message` Pine Logs CSV exported, 69 records parsed and 4C results independently reproduced. See [acceptance report](CISD_V2_PHASE2D_ACCEPTANCE_20261120.md). This remains a research-export utility, not a detector update or trade signal.

## Why this collector exists

TradingView Essential may not offer **Export chart data**, so the Phase 2C numeric plot/CSV method cannot be the only export mechanism. TradingView's official docs explicitly support Pine Logs from **personal scripts**, on historical bars and in Bar Replay, and display up to 10,000 historical logs. See [official support](https://www.tradingview.com/support/solutions/43000710876-i-d-like-to-learn-more-about-pine-logs/) and [Pine Logs v6](https://www.tradingview.com/pine-script-docs/writing/debugging/#pine-logs).

The user's TradingView Essential Pine Logs panel **successfully exported a native two-column `Date,Message` CSV**. The Python importer supports that observed format (and pasted text), including a Replay-specific `syminfo.tickerid` envelope. CSV export behavior may vary by UI version; the specific observed setup is accepted. No subscription change is needed for this research.

## Added 4F inputs (opt-in)

| Input | Default |
|---|---|
| Logs: emit closed-bar CISD events | OFF |
| Logs: from UTC (inclusive) | 2026-11-16 00:00 UTC |
| Logs: to UTC (exclusive) | 2026-11-21 00:00 UTC |
| Logs: include V2 terminal lifecycle events | ON |

In Pine, only after the existing legacy and pivot-V2 detectors have run, and only on `barstate.isconfirmed`, the exporter logs each recorded **confirmed** CISD event for that exact bar. It optionally logs V2 terminal lifecycle events `PIVOT_BREACH`, `EXPIRED`, `SUPERSEDED` and `INVALID_AFTER_CONFIRM`. It does **not** backdate a confirmation to the pivot's originating bar or use future price to decide eligibility.

Log payloads use machine-readable `CISDEVT1|key=value|...` lines with **UTC close epoch milliseconds** `close_ms`, symbol, TF, source, side, reference level, chart-bar OHLC and relevant pivot/ATR metadata. The TradingView Pine Logs UI prefixes its own chart-timezone **bar-opening** time. Never treat that UI prefix as the exact confirmation close; trust the embedded `close_ms`.

Current code retains Phase 2C's `4E` Data Window plots, which default OFF and are not required. `4D` skip diagnostics can remain OFF. No detection threshold, alert, drawing or Po3 decision was altered.

## One acceptance test on Essential (no long Replay session)

1. Preserve saved layouts/presets. Load the new source from `Bandz_Po3_Profiler.pine` in this branch into a **new private Pine Editor script** (published scripts cannot generate logs). Save and Add to chart; send any Pine compiler error text if found.
2. On `FOREXCOM:GBPUSD` / `15m`, keep V2 on, pivot 1 / bridge 2 / scan 12 / min opposing 1 / expiry 10 / ATR gate ON at 0.5; legacy Standard / min 2, as previously frozen. **4D OFF**. **4F Logs ON**.
3. Use start/end UTC **2026-11-17 00:00** to **2026-11-19 00:00**. Prefer normal historical chart (rather than Bar Replay) with those bars loaded; no candle-by-candle stepping is required. Ensure **the date range and chart bar data are loaded**.
4. Open Pine Editor > More > **Pine Logs** (or indicator status-line > More > Pine Logs). Select **this personal script** in the logs selector. Use pane search `CISDEVT1` to remove other chatter. Check for `kind=CONFIRM` records from `engine=V2` and `engine=LEGACY`.
5. **First validation:** find a logged V2 bearish confirmation near `2026-11-18 07:30 UTC` at reference `1.31889` and a legacy bearish confirmation near `07:15 UTC` at the same level. If none, check source feed, V2 switches, loaded history and any removed/changed inputs.
6. In Pine Logs, **export the log entries as CSV** and upload the resulting `Date,Message` file. This was verified on Essential on 2026-11-20. Text pasted from the panel also remains supported. The raw Replay feed ID is ephemeral; do not commit the raw user export to a public GitHub repository.
7. Convert the native CSV or pasted text into normalized event CSVs:

   ```bash
   python3 research/parse_cisd_pine_logs.py /path/to/pine-logs.csv
   ```

   The script generates `pine-logs.events.csv` and `pine-logs.compared.csv`. Run from repository root; Python 3.10+ recommended.

### What this does and does not validate

- Mechanically compares Bandz legacy and V2 on **same TV feed and 15m candle close**; first exact direction/timestamp matches, then adjacent 15m close near-level matches.
- V2 terminal cases are **recorded separately**, not counted as new confirmed CISDs.
- It cannot label an event as **Cephxs validated** because the private Cephxs event stream is unavailable in Pine code.
- FTMO/MT5 has a **different feed**. M1 OHLC can be collected as context and re-aggregated to M15, but never merged as exact price-by-price reference data for FOREXCOM signals.
- A confirmed CISD is an **event**, not a profitable trading setup. No look-ahead comparison of later price swings is used to select detector parameters.

## Frozen snapshot before this branch

Nov 19 2026 4C comparison, GBPUSD 15m bounded Nov 17 10:30–Nov 18 10:45 UTC: `EXACT=5`, `V2_ONLY=5`, `LEGACY_ONLY=2`, `TIME_DIFF=1`, `LEVEL_DIFF=0`, `STAMP=0`. Eight screenshot-derived discrepancy rows are in `research/fixtures/GBPUSD_20261119_4C_WINDOW_DISAGREEMENTS.csv`. The most informative pending investigation is **BEAR V2 Nov 18 07:30 vs Legacy 07:15 at the same 1.31889 level** and the Nov 17 20:00 legacy-only signal with nearby V2 `PIVOT_BREACH` rejection. We should assess **lateness and false negatives**, not reflexively reward greater signal counts.

## The November 19–20 chart supplied by user

The GBPUSD 15m chart uploaded Nov 20 at 13:50 UTC shows a visually useful example of Bandz bearish delivery markup, annotations around SMT, a drawn short risk/reward region and higher-timeframe candle visualization to the right. Those are **qualitative chart context**. Do not infer execution, an independently validated Cephxs match, or a measured edge from colored profit/risk rectangles or projected HTF candles. Displacement following a marker is retrospective evidence and is not automatically a qualifying entry.

## Phase closure criteria

**All three acceptance criteria passed on 2026-11-20.** Pine v6 compiled, the 07:15/07:30 event pair was reproduced, and the full native Pine Logs CSV was exported and parsed. This Phase 2D data-collection stage is complete; proceed to offline cause analysis rather than more screenshot ping-pong.

The subsequent work is a **new** exercise: bounded event evaluation and then V2C improvements to candidate construction after fixing the measured late/omitted classifications.
