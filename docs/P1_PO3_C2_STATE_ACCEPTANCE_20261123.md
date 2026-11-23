# P1 — Po3 / C2 event-state verification (23 November 2026)

## Purpose and source separation

This is a **read-only audit build** for Bandz Po3 V2. It is not the clean trading-test indicator. The original [Bandz_Po3_V2_Visual_Test.pine](../indicators/Bandz_Po3_V2_Visual_Test.pine) is **unchanged**. Full CISD research and original legacy references remain preserved on their own branches.

- Audit script: `indicators/Bandz_Po3_P1_C2_State_Audit.pine`.
- Branch: `feature/p1-po3-c2-state-audit-20261123`.
- The only change to the base prefix is the indicator title. The P1 audit is appended after all full Bandz Po3 / Legacy / V2 code.
- P1 is **OFF by default**. There is no `alert()`, `alertcondition()`, journal integration, order entry, or change to detector thresholds.
- P1 first implementation supports **Chart** sequence-CISD slot only (chart timeframe 15m + higher-timeframe profile is supported). On a chart below 3m/5m with a lower-timeframe sequence slot selected, the chart-CISD qualification deliberately does not trigger.

## What the code actually does (verified from source)

1. **The original Po3 C2 detector**, `poEvalSide()`, allows a still-forming HTF C2 after an open-inside-C1 plus sweep, even before it has closed back inside C1. In the initial bar its phase may still be 2.
2. **The original event record**, `poSyncRecs()`, can clear a previously linked CISD if the growing C2 later extends its sweep extreme. The drawing state therefore cannot directly serve as a durable alert proof.
3. **Legacy chart CISD** and **V2 chart CISD** feed `poLinkCisd()` slot 0; V2 only on a chart bar close. The level may be drawn at an opposing-run origin candle that predates the actual confirmation. This **must not** be interpreted as an earlier event time.
4. P1 snapshots the selected raw CISD's exact `time_close` on its **confirmation bar** and uses the existing record identity (C2 start time and direction) for matching.
5. A new **C2 confirmed** state is observed only if the **chart bar itself has closed**, its close timestamp equals the **source HTF candle close**, and the *live current* C2 closes strictly inside C1 (`sq.closedIn`). No future bar is used to certify that close.
6. A later **C2+CISD qualified** state requires the same original C2 record to still be active, the existing chart-slot CISD link to point at a matching raw closed-bar signal, and `poRecVisible(rc)` to allow the record under the original sequence-direction, PSP and xC2 visibility controls, **with no prior close-back-through reclamation recorded**. The qualification time is the **first chart close at which all these are true**, not the C2 start time or CISD origin time.
7. If a prior linked level is lost before C2 qualification, the provisional P1 link is cleared. A qualified event can subsequently be marked ended if the original CISD is reclaimed/its link ends. An HTF close skipped by a session gap is marked **UNVERIFIED**, not silently backfilled.

### Intentional distinctions

| Audit value | Meaning | Not equivalent to |
|---|---|---|
| `C2 start UTC` | Historical open timestamp of the relevant HTF candle | First time the sweep became visible |
| `First seen UTC` | First closed chart bar at which P1 actually observed this C2 sweep | The HTF candle open or a reconstructed earlier signal |
| `LIVE` | Candidate C2 swept C1 within the still-forming source candle | Confirmed Po3 setup |
| `CLOSED PASS` | That HTF C2 closed strictly back inside C1 | Full model entry or qualified T-Spot |
| `REJECT` | C2 swept C1 but finished outside the required C1 bounds | CISD detector failure |
| `PROVISIONAL` | Raw CISD was confirmed and linked while C2 was still live | Qualified C2+CISD event |
| `QUALIFIED HH:mm` | C2 is HTF-confirmed and its selected raw CISD is linked with original visibility gates satisfied | An instruction to open a trade |
| `ENDED HH:mm` | Reclamation / link loss after qualification, or later original sequence termination | Loss or stop-out |
| `UNVERIFIED` | HTF closing transition was not observed at a chart close (e.g. gap) | Positive or negative C2 result |

The original 4H/1H or 6H/90m profile selection matters. The audit's C2 time is based on **the actual selected source timeframe**, not an assumed fixed 4H.

### November 23 Replay finding

User screenshots captured a bearish 4H C2 starting **2026-11-23 06:00 UTC**, first observed **06:15**, with a **09:15 UTC** chart CISD confirmation. C2 changed from LIVE to **CLOSED PASS at 10:00 UTC** but the initial P1 table still read PROVISIONAL. This is **not enough to conclude** that the qualification engine is broken: it also requires `rc.alive`, the original raw-CISD link, no reclaim, and `poRecVisible(rc)`. The initial UI collapsed all non-qualified scenarios into PROVISIONAL.

The audit-only build now prints `BLOCKED: <reason>` for CLOSED PASS but unqualified C2, including `PO3_VISIBILITY_GATE`, `RAW_SIGNAL_MISMATCH`, `CISD_RECLAIMED`, `NO_ORIGINAL_LINK`, or `ELIGIBLE_NOT_PROMOTED`. It also distinguishes `ENDED / UNQUALIFIED` from genuinely provisional signals. This changes only how the audit reports status; it does not change Po3 or CISD output. Ask for just one further screenshot of the `11-23 06:00 BEAR` row with the new diagnostic; do not repeat the entire sweep test.

## Short TradingView Replay acceptance plan

1. **Preserve** your existing layout and `Bandz Po3 V2 Visual Test` indicator and template. Do not overwrite them.
2. Open the new P1 audit Pine file in GitHub, copy Raw contents to a **new** TradingView Pine indicator, name it `Bandz Po3 — P1 C2 Audit`, and add it to a temporary chart layout.
3. Start with `FOREXCOM:GBPUSD`, **15m**, `Chart CISD engine=V2`, `Sequence CISD from=Chart`. Use your normal HTF ladder, but record the **actual 'Profile on'** source timeframe shown in Bandz's header. A fixed `4H / 1H` ladder with source HTF 2 is convenient for observing 4H C2 closes.
4. Turn ON `P1 · Po3/C2 lifecycle audit → Show Po3/C2 lifecycle audit`. Leave `Recent C2 records=6`. Set chart timezone to UTC for easy alignment with the panel. The panel itself always labels UTC.
5. Replay from just **before a C1 sweep starts**, with **at least one closed source HTF candle of prior context**. Advance in 15m increments, checking the last chart close before the source HTF candle closes. **LIVE** (or **PROVISIONAL**) is *not* qualified.
6. Advance through the **source HTF candle's closing 15m bar**. It must show **CLOSED PASS** or **REJECT** based on the final C2 close back into C1. If no final close can be observed, it must remain **UNVERIFIED**.
7. Check the **CISD close UTC** separately from C2 start and close. **QUALIFIED** should only appear at or after both underlying confirmations, and only when the original Bandz sequence remains eligible.
8. Optionally repeat with `Chart CISD engine=Legacy` using the **same** source timeframe and Replay window. Do not compare levels as if every Legacy and V2 raw event had to match.

### Bounded evidence request

One **valid C2 with selected-engine CISD**, one **candidate that fails or remains unqualified**, and, if visible, one **provisional link cleared by a later C2 extreme** are enough to decide whether this P1 event design is sound. Share just the chart + P1 table at the decisive close(s); **do not** send another week of screenshots.

For known raw V2 examples from earlier work, `2026-11-17 07:45 UTC` bearish and `2026-11-18 07:30 UTC` bearish are useful checks of raw CISD timestamps, **not prevalidated C2-qualified examples**.

## Engineering checks and limitations

- CI checks that the **entire original computational source** is byte-identical (except the indicator title) before the appended P1 audit.
- CI checks that the new block cannot mutate existing `PoRec`, `PoSeq`, `poCisds`, or `v2rEvents`, and has no alert calls.
- Seven **synthetic reference scenarios** test the intended event-state contract. These do **not** run Pine code and cannot replace the native TradingView compile / Replay test.
- Initial P1 panel does **not** constitute a production alert implementation. Real-time / TradingView Replay event order and session gaps must be verified before a qualified alert can use these snapshots.
- **No strategy edge or profitability has been established.** This audit concerns event-time integrity, not forecasting outcomes.

## Exit criteria for P1

1. Native Pine compile succeeds.
2. C2 **cannot** become qualified solely from a live-candle sweep.
3. The same 4H or 90m C2 cannot confirm twice, and a rejected C2 cannot become qualified retrospectively.
4. Raw CISD confirmation time matches the actual chart candle CLOSE, not the start of its drawn reference line.
5. When C2 makes a new extreme and the original engine clears a link, the provisional record does not persist into qualification.
6. Cross-source chart / HTF time alignment is correct in Replay, including a session boundary example or an explicit UNVERIFIED result.

Only after these pass do we move into P2 alert events.
