# CISD v1.3 — Independent FVG lifecycle, CISD context and C2 closure

**Status:** Draft research code. Source checks only; compile and Bar Replay still required. This feature branch is stacked on **v1.2** (PR #2), which itself is stacked on **v1.1** (PR #1). No changes to `main`.

## Scope / what remains unchanged

Do not replace the original Bandz Po3 algorithm: `poEvalSide`, `poSyncRecs`, `poCisdInvalidate`, `poLinkCisd`, its existing entry-FVG overlays and projections are unchanged.

This commit adds an **independent, confirmed-chart-candle research registry** for ordinary three-candle FVGs and links them to retained CISDs. This is **not** a reconstruction of Cephxs proprietary rules and **not** a Propulsion Block detector.

The additional research registry runs only when the chart is in **`CISD = All + C2 highlighted`**. The already-existing CISD history works in the same way as v1.1/v1.2.

## Event semantics — critical distinction

A CISD is historically **confirmed** when its qualifying candle closes through Bandz's reference delivery-run opening price. Once an event is recorded, its confirmation time and price never change.

A later close in the opposite direction through the same CISD level constitutes a **level reclaim / invalidation under Bandz's legacy rule**. This changes the *event status*, but **does not erase that it occurred**. It does not on its own prove that the original trade thesis failed; structural confirmation and ongoing delivery require their own rules.

For a bullish FVG, the completed third candle has `low > high[2]`. The chart-timeframe zone is `[high[2], low]` and the mid is its 50%. For a bearish FVG, it has `high < low[2]`, zone `[high, low[2]]`, mid 50%. All three defining candles are closed when the third candle confirms the FVG. Detection has **no displacement/volume/POI/size filter** yet.

Every retained research FVG records the original direction, confirmation candle and close timestamp, zone top, bottom and midpoint, plus **first subsequent closed chart bar** meeting each condition:

| FVG event | Bullish FVG | Bearish FVG |
|---|---|---|
| First tested | Future bar trades anywhere into zone | Same |
| Midpoint wick reached | `low <= midpoint` | `high >= midpoint` |
| Midpoint adverse close | `close < midpoint` | `close > midpoint` |
| Invalidated across far edge | `close < bottom` | `close > top` |

The close-through tests are explicitly *adverse* to the original FVG direction. The presence of a wick test does not equal invalidation. A far-edge close is tracked as a separate status. Research FVG history is **not removed** at its first invalidation; tracking of later tests stops because this is a *first-event lifecycle*, not a complete retest ledger.

## CISD–FVG association

The first confirmed **aligned** and **opposing** FVG is recorded independently for each CISD when its FVG confirmation candle falls within the configurable window of **2 bars before through 4 bars after** the CISD's confirmation bar. These windows are hypotheses for replay comparison, not known Cephxs rules.

- Earlier FVGs are eligible only when not already invalidated at the CISD close.
- Same-candle or later FVGs enter the record only after their **own** third confirmation candle closes; the FVG is never treated as known earlier.
- A historical CISD annotation may later show an FVG as **`+2 bars`**, meaning the FVG became known two chart candles *after* the original CISD. In live trading, there is no `+2` context available at the original CISD confirmation.
- This classification is *directional and temporal*, not proof that an FVG caused a move or is technically meaningful. No replacement entry signal is introduced.

## Live C2 association versus subsequently qualified C2

v1.1's `c2Linked` remains a snapshot of the **first chart CISD linked to a live C2 candidate**, not a confirmed closed C2. v1.3 records `c2ClosedAt` only when the source sequence later satisfies Bandz's own closed C2 condition (sweep + close back within C1), evidenced by `rc.maxPhase >= 3` with a C3 open timestamp. It records **the C3 open = the preceding C2 close** in the source profile timeframe.

The C2-closed timestamp is a retrospective fact only when it becomes known after C2 closes. It does **not** prove that a previously linked CISD was still attached/active when that closure occurred: Bandz can void a CISD if C2 later makes a new extreme.

## Settings: `4 · CISD + STDV`

Enable `CISD = All + C2 highlighted` to use these new v1.3 research settings:

| Setting | Default | Purpose |
|---|---|---|
| Research: FVG lifecycle zones | **Off** | Draw standalone chart-timeframe FVGs (distinct from original Entry FVGs) |
| Research: FVG lifecycle labels | **Off** | Label each shown FVG's first test, midpoint wick, midpoint adverse close and far-edge close |
| Research: draw FVGs | 6 | Max visible FVG zones; maximum allowed 12 |
| Research: retain FVGs | 80 | Stored FVG events; allowed 10–120 |
| Research: FVG zone bars | 24 | Cap on length of each FVG drawing, 3–200 bars |
| Research: FVG bars before CISD | 2 | Historical preceding FVG association window |
| Research: FVG bars after CISD | 4 | Future FVG association window (no lookahead during replay) |
| Research: include FVG/C2 context in Full labels | **Off** | Adds aligned/opposing FVG bar offsets and C2 closure timestamp to already enabled CISD **Full** labels |

FVG drawing uses a light color-coded historical box plus a dotted midpoint. If price later closes through the far side, the historical box is faded and ends at the recorded invalidation candle, subject to the chosen max zone length. Boxes are *visually anchored to the first defining candle* for context, but **only become visible after the third defining candle closes**.

The chart FVG boxes do not apply v1.2's CISD killzone/context filters. They are independent objects intentionally, so an FVG outside the selected CISD window is not silently dropped.

All FVG and C2 diagnostic controls are optional and drawing-label limits are separate from CISD labels, although Pine's global drawing-object quotas still apply. Use small draw limits when other Po3 overlays are on.

## Manual TradingView acceptance checklist

**Use a new script instance. Do not overwrite the previously working v1.2 indicator.**

1. Compile Pine v6. Copy compiler errors verbatim if any.
2. Set EURUSD (same exact feed) 15M with Bandz profile 4H, `CISD = All + C2 highlighted`, `Research: draw filter = All`. With FVG zones, labels and Full-context disabled, compare against v1.2 at the same Bar Replay endpoint: existing CISD levels, classifications, invalidations, C1/C2/phase, and STDV must remain identical.
3. Turn **FVG lifecycle zones** on, draw 6, zone bars 24. Locate the October 14, roughly 02:30–04:00 New York session bearish CISD/FVG example (`Case CISD-001`). Check gap direction and zone boundaries. You may need to switch `Research: draw FVGs` up to 12 or move Replay closer to that date because the renderer selects the newest 6 *retained* gaps.
4. Enable FVG lifecycle labels. Read confirmation timestamp, test timestamp, midpoint wick, midpoint close, and far-side close. Verify the bearish FVG is **not** marked invalidated merely because a wick touched its midpoint.
5. Rewind to just before the third candle of the bearish FVG. Advance bar-by-bar: no FVG appears until the third candle CLOSES. Its zone may anchor to candle #1 after confirmation; no signal may be visible at candle #1 in the replay before candle #3 closes.
6. Enable `Research: diagnostic labels`, `label verbosity = Full`, `label events = All`, `include FVG/C2 context in Full labels = On`. Verify first aligned/opposing FVG offsets and C2 context appear, and that later `+1` through `+4` FVGs are added only at the appropriate subsequent close. Also verify no retroactive change to CISD origin/confirm/price.
7. Compare the October 14 bearish CISD historical confirmation with FVG activity. Confirm that a reclaimed CISD remains in registry when `Research: faded invalidated CISDs = On`, independently of whether its linked bearish FVG remains active.
8. Verify that switching `Research: draw filter` among All, C2-associated, Killzones and combined still affects **CISD lines only**, while the independent FVG registry/boxes remain unaffected.
9. Recheck a C2-linked event during an *open* 4H candle: it must NOT be reported as **C2 closed** prematurely. Advance through 4H closure, then confirm C2 state updates only when the existing Po3 engine recognizes a valid closed C2.
10. Test GBPUSD and one additional day with dense FVGs, including toggling zones/labels and changes to retention. Watch for runtime errors, overlapping labels, object-limit issues, and performance regression.
11. Reconfirm original Bandz `Sequence only` and `All` drawings match v1.2. New feature must have no visible effect in these modes.

## Constraints and deferred work

- These are **chart-TF raw FVGs**, not MTF FVG, OB, Propulsion Block, or a displacement-qualified gap.
- First association per direction within a window is a *candidate*. We do not yet score risk, entry quality, displacement, liquidity sweep, SMT, or how the FVG relates to a particular C2's price range.
- A C2 closure confirmation is a **later state** and may not validate the specific previously attached CISD.
- The chart's 15M timestamp of gap confirmation can differ from a HTF's FVG boundary.
- No exported alerts or webhook payloads are modified.
- No Pine compiler or historical visual backtest has been run in the GitHub integration. The user must compile and validate in TradingView before merge.

## PR stacking

PR #1 v1.1 → PR #2 v1.2 → v1.3 PR. Merge oldest first **only when** each is validated. Stacking keeps unrelated changes out of each PR diff.
