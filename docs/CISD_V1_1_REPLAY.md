# CISD v1.1 — confirmed history and diagnostic view

Status: **Draft. The initial CISD v1.1 build was compiled and its Active → Invalid transition observed in TradingView; the subsequent label-polish commit still requires compilation and replay verification.**

## Scope

This is an additive research feature. The existing Bandz CISD trigger conditions, C1/C2 sequence engine, SMT, PSP, T-Spots, projections and alerts are **not changed**.

In **4 · CISD + STDV**, select one of:

- **Sequence only** (legacy default): original, sequence-linked CISD rendering.
- **All** (legacy): original current/retained raw CISD rendering.
- **All + C2 highlighted** (new): render a bounded history of confirmed chart-timeframe CISD events; emphasize the first chart CISD linked to a live C2 sequence.

The new mode distinguishes:

- **C2-linked:** thicker original-direction line (linked through the existing first-chart-CISD mechanism).
- **Raw/unlinked:** thin, subdued line.
- **Subsequently invalidated:** faded line when `Research: faded invalidated CISDs` is enabled.

These event classifications are **descriptive, not trading recommendations**. "Raw" can be legitimate; "C2-linked" does not imply the signal is profitable or the underlying C2 correct.

The event registry stores: side, origin chart-bar index, confirmation chart-bar index and **candle-close timestamp**, price level, C2 linkage and C2 source start time (if linked), plus the first later chart-bar close that crossed back through the level. When `time_close` is unavailable (e.g. certain non-time-based charts), timestamps fall back to bar-opening time.

## Inputs / limits

- `Research: retain events` (10–250; default 100): upper bound on stored confirmed events. Oldest events are evicted.
- `Research: draw events` (1–40; default 20): separate cap on lines actually shown.
- `Research: faded invalidated CISDs` (default on): controls display only, **not invalidation recording**.
- `Research: diagnostic labels` (default off): global checkbox for research annotations in the new view. When enabled, the label controls below apply.
- `Research: label verbosity` (default **Compact**): **Off** = no labels; **Compact** = one short two-line annotation at confirmation (direction, C2/raw, timestamp, price, active/invalidated); **Full** = the original detailed confirmation label plus an **O** marker on the origin bar.
- `Research: label events` (default **C2-linked only**): label **All**, **C2-linked only**, or **Invalidated only** events. This does not change which CISD lines are drawn. To review raw detection and invalidation cases like the October 8–9 replay, change this filter to **All**.
- `Research: max labels` (1–20; default **6**): limit the number of most-recent eligible **drawn events** that receive annotations. Labels and lines have independent limits; Full mode consumes two TradingView label objects per annotated event.

The new mode skips events whose origins are more than 4,800 chart bars back so `xloc.bar_index` drawings remain in TradingView's valid range. History retention does not imply perpetual on-chart display. Drawing limits are shared with other Bandz modules; lower the draw cap or disable overlays if the overall chart approaches TradingView's 500-line/500-label limits.

Only **chart-timeframe** raw CISDs are recorded in this new registry. Existing 3m / 5m sequence association, when applicable, remains in the legacy engine and is not converted into independent history records.

## Non-repainting expectations and caveats

New history events are appended only after the **chart candle closes** (`barstate.isconfirmed`). Invalidation is the first *subsequent confirmed chart candle close* back through the CISD level, tracked even when the legacy `Remove once closed back through` setting is off.

Historical annotations change when a later candle invalidates an event, because its status becomes *invalidated*. This is expected; the original confirmation time and price must remain unchanged. The two legacy modes have not been changed and may still show developing-bar behavior from the original script.

Replaying on a different ticker feed, chart timeframe, session/timezone, or indicator settings can legitimately produce different raw events.

## Manual acceptance checks (TradingView Pine v6)

1. Open the branch source in Pine Editor as a **separate indicator**. Compile it and record any diagnostics verbatim. Do not replace the currently working Bandz indicator before it compiles.
2. EURUSD, matching feed, 15m chart / 4H profile, preferably Oct 9–16 2026. Set **Sensitivity: Standard**, **Min run: 1**, legacy invalidation **On**. For identical profile sources, turn **Auto HTF/Auto count Off**, use 1H / 4H / 1D lanes, and profile on HTF 2.
3. Verify legacy **Sequence only** against the original public release with no visible differences. Repeat for legacy **All**.
4. Switch to **All + C2 highlighted**. Confirm it draws thin raw levels and thicker first-linked C2 levels while not changing Po3 phase/sequence or STDV calculations.
5. Enable `Research: diagnostic labels`, set `Research: label events = All`, `Research: max labels = 6`, and set verbosity to **Full**. Inspect the origin **O**, confirmation timestamp and price on a clearly visible bullish and bearish CISD. Compare the timestamp with the configured Bandz timezone.
5a. Change verbosity to **Compact**: each eligible event should use only one short label (no **O** marker). Change it to **Off**: all research labels disappear, but lines remain unchanged. The global diagnostic checkbox off must have the same label-hiding effect.
5b. Test **C2-linked only** and **Invalidated only** scopes; verify filtering affects **labels only**, not raw event lines or event history. Try label caps 1 and 3, and compare with `Research: draw events` kept at 20.
6. Rewind Bar Replay *before* the Oct 14 bullish recovery. Advance one closed 15m candle at a time. No event should be added permanently before its confirming close. Its timestamp and level must stay fixed after subsequent bars.
7. Let price close back through a previously confirmed CISD. Confirm it fades, and shows the **first** invalidating close in diagnostics. Toggle `Research: faded invalidated CISDs` off and verify it disappears **from the research view**.
8. Change `Research: retain events` and `Research: draw events` independently. The latter should not affect which newer events survive in the registry.
9. Check a long history and an active liquid market for runtime errors, object-limit warnings and excess latency.
10. Repeat on at least one additional instrument (e.g. GBPUSD or XAUUSD) and both bullish and bearish movements before approving a merge.


## UI polish (post-initial replay)

The October 8–9 screenshots demonstrated working C2-linked/raw lines and an apparent Active → Invalid transition, but Full labels overlapped when many nearby CISDs were drawn. Compact mode, event-scope filters, and a label cap address the presentation only. **These newer controls still need to compile and be exercised in TradingView before merging.**

## Deferred work

Not included: alternative CISD detection formulas; Cephxs size-filter inference; new same-timeframe Po3 support; expanded C1/C2 history/qualification; Propulsion Block detection; webhook/JSON alerts.

## Rollback

Switch back to `Sequence only` or `All`; the feature adds no changes to those render branches. For a complete rollback, remove the branch-only source and keep using `main`.
