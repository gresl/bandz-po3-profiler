# CISD V2 phase 1 — independent pivot candidate lifecycle

Status: **experimental / opt-in / pending TradingView Pine v6 compilation and Replay acceptance**  
Research branch: `experiment/cisd-v2-pivot-lifecycle-20261115`  
Base branch: `experiment/cisd-pivot-audit-nov2026`

## Source-level comparison (2026-11-15)

Reference Cephxs source is retained separately in **private** `gresl/cephxs-cisd-reference/source/cephxs-cisd-base.pine`. Do not paste the source or private URLs containing tokens into this public repository.

| Issue | Cephxs code observation | Bandz original baseline |
|---|---|---|
| Candidate creation | Pivot high/low with one right-hand bar, maintains pending candidates | Tracks run of same-colored opposing candle bodies |
| Level | First open of initial opposing stretch | First/last open depending on Bandz sensitivity |
| Stretch filter | ATR(14) magnitude, default Regular 0.5 ATR | Min opposing run = 2; no equivalent raw ATR gate |
| Pending lifetime | Standard 10 or Max 20 bars | Run age up to 60 |
| Confirmation condition | `close` beyond level; no explicit `barstate.isconfirmed` in confirmation block | Raw trigger checks `close`; research event registry persists only when `barstate.isconfirmed` |
| Invalidation | Price trades through candidate pivot extreme | Legacy close returns through CISD level |
| Plot time | Line starts at opposing run origin; may precede confirmation | Research lines start at opposing run origin too |
| Later history | Old drawings can be deleted/faded | Separate bounded research history |

Crucial limitation: an early-looking line is **not proof** of early non-repainting confirmation. A Pine indicator may evaluate an unclosed realtime `close`, then rollback on the next tick. Use simultaneous live observations / timestamped alerts for first intrabar availability, not historical bar labels.

## Phase 1 implementation

Bandz now includes the independent group **4C · CISD V2 pivot research (experimental)**. All V2 settings default to disabled or innocuous values; enabling V2 does NOT change `poCisds`, `poCisdEvents`, `poLinkCisd`, C2/C3/C4, T-Spot, STDV, alerts or existing webhooks.

The independent detector:
1. Recognizes a pivot high/low only after the configured right-hand chart candles CLOSE (default 1).
2. Looks backward a bounded distance to find a consecutive opposing candle-body stretch. A short non-matching bridge to the pivot is permitted but not included in stretch length.
3. Registers a candidate at the **pivot-recognition close**, never at the pivot's earlier bar. Captures the initial run-open reference and pivot extreme.
4. Replaces an earlier still-pending candidate of the same direction when a newer eligible pivot appears. Stores SUPERSEDED as a terminal state.
5. After each closed candle, evaluates pivot-wick breach first, then expiry, then close-through-level confirmation. A candidate may confirm on the same close it was created if all information was available by that close; no artificial extra 15m wait.
6. Preserves confirmed time and price when the pivot extreme is later breached; later invalidation is a distinct state.
7. Displays only contemporaneously known pending levels and confirmation triangle markers; a bounded **top-left** event table shows recent candidates with first-known and confirmed UTC closes. No backdated line anchors.
8. Retains at most 80 candidates; panel shows 8 most recent including rejected/superseded. This is a diagnostic cap, not complete event-history export.

Default: pivot left/right = 1, bridge = 2, additional scan = 12, min run = 1, expiry = 10, optional ATR stretch gate OFF (threshold 0.5 when enabled). These are **untuned hypotheses**, not recommended entry settings.

## Methodology and acceptance gates

- **Code review:** compare opt-in V2 code against the previous branch; old CISD/Po3 logic unchanged.
- **Synthetic tests:** `python3 -m unittest discover -s research/tests -v`. The independent Python oracle reproduces *designed* transitions on synthetic OHLC; it is not a Pine compiler and does not prove true broker/feed parity.
- **TradingView compilation:** copy `Bandz_Po3_Profiler.pine` from this branch to a **new** Pine editor script, compile. Report the exact first error and line if any. Do not overwrite saved Preset A / original Pine copy.
- **OFF regression:** with V2 disabled confirm same legacy C6 audit event at GBPUSD 2026-11-11 05:45 UTC, level 1.33454, and no V2 overlays.
- **ON research:** enable only V2 / registry, retain Bandz legacy CISD and Cephxs reference inputs. Compare exact UTC close times, not origin bars. Verify candidate known-time is >= pivot recognition close, confirm is >= known-time.
- **Historical fixtures:** use the authorized exact feed/timezone/15m OHLC; capture positive, negative and near misses. Never label a gap between drawings as 15m delay without verified close timestamps.
- **Live observation:** compare realtime behavior separately. V2 confirmation is deliberately close-only; Cephxs may display provisional intrabar signals. Do not equate any intrabar preview with a confirmed non-repainting event.
- **No trade quality inference:** only after mechanical reproducibility should Po3/CRT/session qualification or outcomes be evaluated.
- **No merge to main** until compilation, Replay and off-mode regression pass.

## Open issues

- The Python oracle models strict pivot comparisons; Pine's `ta.pivothigh/ta.pivotlow` may handle equal-high/low ties differently. Test tied pivots explicitly.
- Pine source is uncompiled here. Native TradingView is required for script compile and runtime validation.
- Current prototype intentionally does not include an *intrabar* early-preview state, to keep the first research pass non-repainting. It can be added as a separate explicitly provisional visual after close-only behavior is stable.
- The exact 2026-11-11 Cephxs timestamp cannot be reconstructed from the historical line anchor alone.

## TradingView acceptance checkpoint — 2026-11-16

User reports that the integrated experimental V2 Pine script **compiled successfully in TradingView** and that its V2 registry/markers render on GBPUSD 15m. User supplied chart screenshots taken 2026-11-16 18:49–19:03 UTC.

At the GBPUSD November 11 historical replay endpoint, the V2 registry visibly shows a **BEAR / 1.33454 / first-known 2026-11-11 05:45 UTC / confirmed 2026-11-11 05:45 UTC**. The independent legacy C6 fixed-time audit shows the 05:45 UTC bearish event at the same level. This verifies a close-time and price-level consistency for **one** event; it does **not** establish correctness of all V2 signals or parity with Cephxs.

The raw V2 defaults (minimum opposing-run length 1 and ATR stretch filter off) produce numerous additional confirmations, including small-stretch candidates. Do not silently interpret signal count as a performance improvement.

**Outstanding:** preserve the raw A configuration as TradingView template and separate chart layout; compare one parameter at a time (first min run 1 vs 2, *without* enabling ATR filter simultaneously); inspect both bullish/bearish positive examples and negative controls; verify event state transitions under advancing Replay. No Pine source changes required at this checkpoint.


## TradingView acceptance checkpoint — 2026-11-16 experiment MinRun 1 vs 2

User tested `FOREXCOM:GBPUSD` 15m around the November 11 05:45 UTC event with an unchanged Replay endpoint, legacy Bandz audit still visible. Two comparison screenshots were provided on November 16 at 19:03 and 19:15 UTC.

| Event UTC on 2026-11-11 | V2 raw MinRun=1 | V2-B MinRun=2 |
|---|---|---|
| BEAR 03:45, level 1.33475 | CONFIRMED | CONFIRMED |
| BULL 05:00, level 1.33471 | CONFIRMED | No longer in recent V2 history / no corresponding marker |
| BEAR 05:45, level 1.33454 | CONFIRMED | CONFIRMED |
| BULL candidate known 04:15, level 1.33533 | SUPERSEDED | PENDING |

All other parameters were intended to remain fixed: pivot 1, bridge 2, scan 12, expiry 10, ATR gate OFF. New screenshot did not separately show the input panel, so changes are inferred from the instructed single-parameter procedure and effects; explicitly reconfirm if behavior disagrees in subsequent tests.

Interpretation: fewer signals with MinRun 2, but NOT proven higher validity. Pending-event survival also changes; registry only displays latest eight candidates, so do not compute frequency statistics from rows alone. The Nov 11 05:45 bearish event is still first-known and confirmed at 05:45 UTC — no proven early warning. Next experiment isolates ATR filter against **original MinRun 1**, not stacked on MinRun 2. Keep both baseline snapshots saved before changing settings.
