# M0 — Cephxs CISD [base] parity before our engine port

Status: baseline research only; **no Pine changes**, no confirmed matches, no performance claims.
Base branch: `feature/pb-v0.1-research-spec` (PR #11); independent of experimental PR #12.
Target publication: https://www.tradingview.com/script/zzL17fzY-cephxs-CISD-base/
User-supplied study reference: `cephxs_cisd.pine` (671 lines), SHA-256 `219db913cf3cd9076bba58cf8086cd5021beaa15bdec537bbaaaaf1c0c0cf07e`. **Not copied to public repository.**

## Objective and evidence hierarchy

M0 tests whether the published Cephxs CISD [base] engine produces the same regular CISD and thin-line PB markings as Cephxs Po3 [Ultimate+] for relevant historical events. Source-code similarity alone does not prove Ultimate+ parity. Record first *knowable* confirmation CLOSE and distinguish it from the origin/pivot timestamp and from indicator rendering. Phase C6 Bandz and the original, uncompiled PR #12 prototype are unchanged.

Observed open-source [base] algorithm (user-supplied code):
- Pivot high/low of length 1; walk back an opposing body stretch and select the first opening price as level.
- Pending dots have a 10-bar Standard/20-bar Max timeout; a close beyond the level confirms regular CISD.
- Thin 1px PB mark: a new confirmed same-direction CISD whose opposing run extreme lies inside the zone of a preceding confirmed same-direction CISD, aged at most the pending timeout.
- Active CISDs invalidate if price crosses the associated origin pivot; historical mode can retain invalidated lines.
- **Code review issues, not verified defects:** runtime confirmation block is not explicitly gated by `barstate.isconfirmed`; when historical retention is ON, PB scanning does not check `ci.is_invalidated`. Test the unmodified baseline before changing either.

## M0a — TradingView first-pass settings

Symbol **FOREXCOM:EURUSD**; normal **15-minute** candles; chart timezone **America/New_York**, 4H Po3 profile in Ultimate+. Exact title/version, feed, settings and Replay endpoint must be recorded.

Cephxs CISD [base] (published script or unmodified local upload):
- CISD Directional Bias = **Auto**; Show CISD = ON;
- CISD Sensitivity = **Standard** (pending 10 bars);
- CISD Size Filter = **ON, Regular**;
- Filter by Purge = **OFF**;
- Show All Historical CISD = **OFF** for first match test (repeat ON separately for invalidation research);
- Show Fibonacci Projections = **OFF** to reduce clutter.

Cephxs Po3 [Ultimate+]:
- CISD visible, Sensitivity = **Standard**, Size Filter = **ON, Regular**;
- Filter by Purge = **OFF**; Filter out Invalidated CISD = **ON**;
- any C2/FVG-only display filters or other visibility controls must be screenshotted and noted (don't assume equivalent switches).
- Do **not** assume Po3 phase state is the same as standalone `Auto` bias.

## M0b — First two comparison windows (NY time, events unverified)

1. **2026-10-08 morning, bullish** — existing research screenshots show C2/CISD and possible PB. Zoom roughly 05:00–11:00 NY.
2. **2026-10-22 early morning, bearish** — prior Cephxs screenshots indicate a candidate thin-line PB near a regular CISD. Zoom roughly 00:00–08:00 NY.

Controls after first two: 2026-09-21 09:00–10:15 NY bearish CISD, 2026-10-16 07:00–11:00 NY bullish CISD, plus one Cephxs regular CISD **without** any thin-line PB.

For **each** window: set Replay one closed 15m bar before visible candidate; screenshot then advance one 15m close at a time until mark first appears. Capture the confirmation bar, +1 closed bar and +4 closed bars, and one wider-context view. Repeat on the same instrument/feed/window with the second indicator. Thin = candidate PB, thick = regular; annotation/line thickness alone does not validate the parent-zone definition.

Record:
- Date and chart feed/timezone/interval, indicator exact name/version/settings;
- direction, origin pivot OPEN NY, level (5 decimals), confirmed candle OPEN and first knowable CLOSE NY, thin vs thick vs absent;
- earlier same-direction active CISD level and pivot / potential PB parent if identifiable, or `unknown`;
- first seen in Replay, invalidated/removed later, changed after indicator reload;
- screenshot filenames plus mismatches classified `MATCH`, `LEVEL_DIFFERENCE`, `CLOSE_TIME_DIFFERENCE`, `BASE_ONLY`, `ULTIMATE_ONLY`, `UNSURE`.

## Acceptance gate: before implementation

- At least 1 bullish and 1 bearish CISD example, with one confidently observed PB and one *non-PB* control.
- Each candidate's confirmation CLOSE is separated from anchor OPEN, and the thin regular/PB visual difference is documented.
- Reload on the same Replay endpoint reproduces the same confirmed historical record, or a precise failure is filed.
- Do **not** infer equivalence from one or two matching pictures; mismatches are expected evidence, not failures to hide.
- TradingView compile status must be explicitly reported for any locally uploaded source. Static inspection does not establish compilation.

## M1 → M4 after M0

M1: isolated copy of properly licensed standalone CISD/PB engine in new file; preserve MPL authorship, verify TradingView republication terms; explicit frozen close timestamps and independent "historical invalidated" regression.
M2: **causal** 15m→NY 4H 01/05/09/13/17/21 candle builder, C2 sweep/reclaim and association, raw CISD unchanged.
M3: configurable 1/5/9 CRT overlays, context tags; displacement/FVG remain measured experimental qualifiers, not hidden changes to raw detection.
M4: +16/+32-bar causal outcomes and Po3 Journal normalized event export; no alerts/execution or profitability claims until separately approved.

## Working agreements

- Keep `Bandz_Po3_Profiler.pine`, Phase C6, PB research PR #11 and alternate prototype PR #12 unchanged.
- New implementation remains on its own branch/PR; compilation and Replay sign-off before any merge.
- No upload of the user's source to a public repo until provenance and publication rights are checked.
- TTrades-style parent-order-block PB (PR #11) remains a **separate** hypothesis from the author-defined Cephxs same-direction CISD-zone PB.
