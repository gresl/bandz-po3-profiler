# CISD V2 Phase 2C — batch event CSV export and offline comparison

**Status:** new research branch, code committed; GitHub Python CI and native TradingView Pine compile remain separate acceptance gates.  
**Parent:** `experiment/cisd-v2-legacy-skip-diagnostics-20261118` (PR #16), which is itself based on Phase 2 disagreement audit (PR #15).

## Snapshot that motivated this experiment

The user shared the chart and a close-up of the **4C · V2 vs Legacy** table taken 2026-11-19 17:17 UTC, with `FOREXCOM:GBPUSD` 15m Replay endpoint `2026-11-18 10:45 UTC`, status `END OPEN`. Bounded comparison starts `2026-11-17 10:30 UTC`:

- `EXACT=5`, `LEVEL=0`, `TIME=1`, `V2_ONLY=5`, `LEGACY_ONLY=2`, `STAMP=0`.
- Eight concrete differences are transcribed from the screenshot in [the 4C window fixture](../research/fixtures/GBPUSD_20261119_4C_WINDOW_DISAGREEMENTS.csv).
- The key timing difference is `2026-11-18 07:30 UTC` BEAR V2 level **1.31889** versus `07:15 UTC` BEAR LEGACY at **the same level**; **do not interpret a later V2 close as better detection**.
- Legacy-only `2026-11-17 20:00 UTC` BEAR at **1.32184** is paired to a *nearby rejected candidate* with `PIVOT_BREACH` note (not proof of causality). This is a valuable potential V2 false negative.
- Internal Bandz classifiers cannot see Cephxs; **all eight remain unverified against independent Cephxs on this screenshot**.

The 5 exact and 8 disagreement categories represent **13 classified pairs or unmatched events within a bounded overlap**. It is not a population performance study or a 13-trade win rate.

## Why numeric chart-data export rather than Pine Logs

TradingView's supported **Export chart data** creates CSV containing values from indicator `plot()` series, including `display.data_window`-only plots; see the official [Indicators FAQ](https://www.tradingview.com/pine-script-docs/faq/indicators/#is-it-possible-to-export-indicator-data-to-a-file). Logging can be used for debugging, but the Pine Logs pane is not an adequate guaranteed bulk CSV output.

Phase 2C adds opt-in `4E · Research batch CSV export (opt-in)`: `Export: numeric event columns in CSV` **OFF by default**. When enabled it adds 10 numeric **Data Window-only plots** (no chart clutter, no detector or alert changes):

| Plot title (stable CSV header suffix) | Meaning |
|---|---|
| `CISDEXP_V2_BULL_LEVEL` | V2 bullish confirmed level on the actual confirmation bar |
| `CISDEXP_V2_BEAR_LEVEL` | V2 bearish confirmed level |
| `CISDEXP_LEGACY_BULL_LEVEL` | Legacy bullish confirmed level |
| `CISDEXP_LEGACY_BEAR_LEVEL` | Legacy bearish confirmed level |
| `CISDEXP_V2_BULL_STRETCH_ATR` / `CISDEXP_V2_BEAR_STRETCH_ATR` | V2 opposing stretch magnitude in ATR14 units |
| `CISDEXP_V2_BULL_PIVOT_BAR` / `CISDEXP_V2_BEAR_PIVOT_BAR` | Originating pivot **bar index** (not a confirmation timestamp) |
| `CISDEXP_V2_BULL_COUNT` / `CISDEXP_V2_BEAR_COUNT` | Number of V2 confirmations on this bar for this side |

Values are `na` otherwise, and are sampled only on `barstate.isconfirmed`. The price series is captured after the existing original detector processing and uses **real stored confirmation bar / timestamp**, not retrospective searches for arbitrary nearby drawings. Fields are numeric and read-only. The chart-data CSV timestamp identifies the **opening** of its 15m candle; the parser converts this into **closing UTC** by adding 15 minutes.

**Known limitation:** A CSV has one row per chart bar; in the rare case V2 confirms more than one same-side candidate on one candle, the first confirmation level is exported and the `COUNT>1` column explicitly flags the record as incomplete. Such collisions must be inspected separately, not automatically scored. Candidate expiry / rejected / superseded lifecycle reasons are **not** included in this minimal numeric export; they remain in the on-chart bounded registry and targeted audit.

## TradingView — one batch, not candle-by-candle

1. **Preserve the saved baseline layouts and scripts.** Use a fresh Pine Editor script sourced from `experiment/cisd-v2-batch-export-20261119/Bandz_Po3_Profiler.pine` in a *new research-only layout*. Set only this new instance visible to avoid duplicate record columns.
2. Keep the known V2 ATR0.5 settings: pivot length 1, bridge 2, scan 12, min opposing run 1, expiry 10, ATR gate ON / 0.5. Legacy Standard/MinRun2. Keep 4C comparison ON if desired; switch 4D single-bar skip panel OFF.
3. Set **4E export ON**. On **FOREXCOM:GBPUSD, 15m** in UTC (normal OHLC candlesticks, not Heikin Ashi), load Replay to beyond November 18 10:45 UTC or use a normal historical chart with Nov 17–18 bars visible. Chart history must include both complete days. No manual stepping for 13 events.
4. Open the **chart layout dropdown → Export chart data…**; select chart and a consistent **UTC/ISO 8601** time format when available. Export CSV. Check it includes `CISDEXP_V2_BEAR_LEVEL` and `CISDEXP_LEGACY_BEAR_LEVEL` columns. **Availability is plan-dependent**, so if this menu isn't present report that rather than purchasing an upgrade just for this research.
5. Run locally in a checkout of this repo (Python 3.10+):

   ```bash
   python3 research/analyze_cisd_batch.py /path/to/TradingView_export.csv --timeframe-minutes 15 --source-timezone UTC --output /path/to/GBPUSD_CISD_comparison.csv
   ```

   Or upload the original exported CSV into this chat, and we can execute the parser without requiring local development steps.
6. If the CSV is from a chart in a non-UTC timezone without an explicit offset, set `--source-timezone Europe/Bucharest` **only if** this is indeed the CSV time zone. If it uses Unix seconds/milliseconds or offset-aware ISO timestamps, the parser honors them directly.
7. Compare the new CSV classifications against the visible 4C screenshot. Differences can be caused by the prior 4C history cutoff, different chart endpoint, feed, indicator settings, or same-bar collisions. **Do not overrule the actual screenshot** without diagnosing the discrepancy.

The batch comparator performs exact-time same-direction one-to-one matching first, then **one-bar-close** nearest-level matching within 20 ticks. Same-close level differences >3 ticks count as `LEVEL_DIFF`. All others are `V2_ONLY` / `LEGACY_ONLY`. It outputs a CSV with both timestamps, prices, V2 ATR stretch and pivot bar and an ambiguity flag.

## Milestone / acceptance

- **Engineering validation:** Native Pine v6 compiles; Data Window plot columns are present; chart-data export includes them; Python tests pass; exported 07:15/07:30 BEAR discrepancy has identical level **1.31889** and one-bar timing difference.
- **Data validation:** At least 15–20 mechanically distinct, frozen confirmation pairs/candidates across several market regimes. Select a small number of genuine asymmetric cases for independent Cephxs Replay visual/confirmation checks. Cephxs agreement is a reference, **not a ground-truth measure of quality**.
- **Algorithm revision:** Do not change V2 inputs on this export branch. First evaluate a potential **V2 false negative** (`LEGACY_ONLY` with `PIVOT_BREACH`) and a timing difference against Cephxs. A candidate that appears late may be inferior even if subsequent price movement looks good.
- **No merge** into main or earlier research branch until compiled and reproducible in TradingView.

## Source references

- TradingView official [Export indicator data](https://www.tradingview.com/pine-script-docs/faq/indicators/#is-it-possible-to-export-indicator-data-to-a-file).
- TradingView official [Pine Logs reference](https://www.tradingview.com/pine-script-docs/writing/debugging/#pine-logs) (useful for debugging but not the primary CSV pipeline).
