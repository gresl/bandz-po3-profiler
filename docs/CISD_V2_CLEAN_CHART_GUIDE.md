# Bandz CISD V2 — clean standalone chart indicator

Standalone source: indicators/Bandz_CISD_V2_Clean.pine
Frozen baseline: experiment/cisd-v2-pine-logs-20261120 / Bandz_Po3_Profiler.pine

## Status

The exact 110-line V2 candidate-generation and confirmation engine was copied unchanged from the frozen baseline. Automated source-integrity tests protect that block. The original frozen V2 script historically matched 17 of its 17 events with the private Cephxs archived-base source on FOREXCOM:GBPUSD M15, plus one extra repeated-level Cephxs event. This new *standalone* script has not yet been compiled or smoke-tested inside TradingView. GitHub/Python CI is not a Pine compiler. Live alerts and trading profitability are not established.

The standalone script is V2 CISD-only. It deliberately excludes original Bandz legacy/Po3/C2, PB, CRT, SMT, research snapshots, CSV exporters and diagnostic tables. Its optional simple event registry is OFF by default.

## Install on TradingView Essential

1. Open indicators/Bandz_CISD_V2_Clean.pine on this branch in GitHub. Click Raw and copy its full contents.
2. In TradingView, open a NEW private Pine Editor script. Paste the source, Save as Bandz CISD V2 Clean — Personal, and Add to chart. Do not overwrite the preserved Bandz research script.
3. Set the chart to FOREXCOM:GBPUSD 15m standard candles. Expect cyan bullish triangles and levels, orange bearish triangles and levels.
4. Save an indicator template named BANDZ - CISD V2 CLEAN - 15M and save the chart layout. Preserve the old RESEARCH - CISD PARITY - 15M - V2 template separately.
5. If compilation fails, send the first compiler message including line and no other debugging data.

## Detection inputs — frozen audited defaults

| Setting | Value |
|---|---|
| Enable V2 | ON |
| Confirmed pivot left/right bars | 1 |
| Bars to find opposing stretch | 2 |
| Maximum additional stretch bars | 12 |
| Minimum opposing stretch candles | 1 |
| Candidate expiry bars | 10 |
| Require minimum stretch / ATR14 | ON |
| Minimum stretch / ATR14 | 0.5 |

Detection code is unchanged. ON and ATR ON input *defaults* are deliberate chart configuration choices matching the audited run, not new optimizations. Adjusting detector parameters changes events; save experiments in other indicator templates.

## Appearance inputs — independent from the detector

| Setting | Default |
|---|---|
| Enable chart drawings | ON |
| Show confirmation triangles | ON |
| Show pending, unconfirmed levels | OFF |
| Show confirmed levels | ON |
| Keep invalidated levels, faded/dotted | ON |
| Show price labels | OFF |
| Display bullish and bearish | Both ON |
| Historical line start | Opposing stretch origin (corrected Nov 20) |
| Max confirmed lines | 60 |
| Confirmed line duration | 20 chart bars |
| Line width | 2 |
| Bull/bear colors | Cyan / Orange |
| Pending/invalidated transparency | 50 / 75 |
| Optional 8-event status registry | OFF |

The default line start is now Opposing stretch origin, using the first opposing-stretch candle's OPEN (event originBar) to show where the V2 level comes from. This fixes the left-side displacement of the clean indicator relative to the original Bandz research presentation. It is a back-anchored historical annotation **created only when the CISD confirms**, never evidence that the confirmation was available at the origin. Selecting Confirmation instead shows only the signal-forward line.

The frozen engine retains its last 80 candidates (including rejected and expired); displayed lines have their own limit. Absence of a historical line does not prove an event was absent.

## Two-minute visual acceptance

On FOREXCOM:GBPUSD 15m, confirm the following events by candle CLOSE time in UTC:

| UTC closing time | Expected signal | CISD reference level |
|---|---|---|
| 2026-11-17 07:45 | BEAR | 1.31911 |
| 2026-11-18 07:30 | BEAR | 1.31889 |

The Nov18 07:15 legacy signal is NOT the V2 expected confirmation. TradingView often labels a chart candle by OPEN time, 15m before its close; do not mistake its opening label for event confirmation time. Reload/re-add and check that the same two signals remain; no elaborate Replay audit necessary.

## Alert options, not yet live verified

- CISD V2 — bullish confirmed CLOSE
- CISD V2 — bearish confirmed CLOSE

After compilation these are separate Create Alert conditions. Configure Once Per Bar Close. These are derived only from V2 closed-bar flags; their levels are supplied via hidden price plots. Historical alerts are not sent retrospectively. Realtime alerts require a separate one-time live check before operational use.

## Preserved source and tests

The frozen core sits between the type PoV2PivotEvent declaration and the float v2rPendingBull declaration, exactly as in the old full Bandz script. Candidate birth, pivot confirmation, opposing-run selection, ATR filter, expiry, breach, supersession, invalidation and confirmation flags are unchanged. Only input defaults, display objects, compact optional registry, and alertcondition outputs were added. The source-integrity CI tests are static and must be followed by one manual TradingView compilation.

## Nov 20 visual anchor correction

A side-by-side comparison of the clean and original Bandz charts showed the *line's left endpoint*, not the reference price level, displaced. This was caused by the first clean indicator defaulting to the confirmation candle while the chart expectation was the originating opposing-stretch candle. Default changed to Opposing stretch origin using the existing frozen V2 event's originBar; **the detector and signals remain unchanged**. Source-identity tests now protect this appearance default. After updating the personal Pine script, save again and overwrite its separate clean indicator template if desired. Existing TradingView indicator instances may preserve the old dropdown setting and will need to be changed manually. No need to redo the 17-event parity study.
