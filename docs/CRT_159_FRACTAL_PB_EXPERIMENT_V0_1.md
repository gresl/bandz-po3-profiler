# CRT 1/5/9 Fractal + CISD/PB — independent research v0.1

**Status:** Uncompiled experimental Pine v6. NOT equivalent to Cephxs Ultimate+, NOT an entry or alert engine.

## Why a separate file?
Our existing Bandz Phase C6 and PB-A design baseline must not change until TradingView compiles and Replay establishes behavior. This prototype studies an alternate definition from Cephxs' **public** standalone CISD publication, while retaining our stricter TTrades/ICT parent-OB PB design as a *different hypothesis*.

## References and provenance
- Cephxs public behavioral explanation: https://in.tradingview.com/script/zzL17fzY-cephxs-CISD-base/
  - This prototype is independently coded from published *descriptions*; **the full Cephxs source code was not obtained or transplanted**. Exact parity is **NOT claimed**. Cephxs calls a PB a later confirmed CISD with a reversal extreme held inside an earlier active same-direction CISD zone. Lines are thin for PB.
- CantoLab fractal model (MIT licensed): https://github.com/cantolab/open-source-fractal
  - Reviewed as an architectural reference, **no source copied** into this prototype.
- User-provided ICT collection: https://github.com/ict2023trader/Indicators
  - Inspected `OpenSourceFractal-Base.pine` and `LatestUpdate/FM-Latest.pine`. Multi-TF options, C5/C6, and event alerts are interesting. Repo had **no root LICENSE** at inspection. No code copied; do not mix files into our GPL/MPL code without permissions/license review.
- Existing Bandz source: `Bandz_Po3_Profiler.pine`, Phase C6 PR #10, PB contract PR #11. **Unmodified.**

## Defined initial model (hypothesis; intentionally incomplete)
- Execution: **15m standard candles**; incomplete/alternate charts are visually warned.
- Higher timeframe: **New York-local 4H windows 01:00, 05:00, 09:00, 13:00, 17:00, 21:00**; handle US daylight-saving via IANA zone. The 01/05/09 time filter is configurable; by default all NY 4H windows are observed to avoid hiding control cases.
- **C1/C2:** Track one fully observed NY 4H candle as C1. A following **completed** 4H candle is bullish C2 if it wicks below C1 low then closes inside above C1 low; bearish vice versa. Label C2 at the actual 4H **close**, not at the candle's opening. This delays C2 identification until HTF close.
- **15m CISD:** Track the first opening price of a consecutive delivery run (at least 2 matching candle bodies). Once the run flips direction, a provisional opposing-direction CISD can be confirmed by a later or same-bar **15m closing** break through that level, within 10 bars. The line is anchored to the older run solely for visual context, but its signal is the later confirmation CLOSE, printed in NY time. This is not a guarantee of exact Cephxs walk-back/swing logic.
- **C2 association:** tag a later CISD if its direction matches a recent completed C2 within 32 15m bars. Default display includes unassociated CISDs as **negative controls**; a presentation-only C2 gate is available.
- **PB? classification:** given an earlier confirmed and still-live *regular* same-direction CISD zone, if the NEW CISD opposing-run extreme enters that zone and holds, draw the NEW confirmation line at width 1 and explicitly label `PB?` (experimental). No original Cephxs PB implementation is claimed; **not the TTrades parent-OB revisit state machine in PR #11**.
- Mark the original CISD line width 3. Research PB candidate is width 1. The PB candle **body midpoint** in the optional diagnostic is the last candle of its opposing run (hypothesis), not the 3-candle FVG midpoint or its confirming candle.
- Parent invalidation is frozen as a later closing break of the earlier opposing-run extreme. Drawn lines are archival, not automatically removed on invalidation in v0.1; cleanup is bounded. Pending levels are not drawn. Thus historical display differs from Cephxs by design.
- No signals, automated execution, webhooks, alertcondition, FVG gate, SMT, projected targets or confidence scores.

## First TradingView compilation and Replay test
1. Open https://github.com/gresl/bandz-po3-profiler/blob/experiment/crt-159-fractal-cisd-pb-v0.1/experiments/CRT_159_Fractal_CISD_PB_v0_1.pine, choose **Raw**, paste all lines into a **new** Pine indicator, and compile.
2. Chart: `FOREXCOM:EURUSD`, **15m normal candlesticks**, America/New_York timezone; the script uses this timezone internally regardless of chart visual timezone.
3. Use default options. Step across a NY 4H **completion** (01/05/09) and verify C2 appears only once the 4H bar closes.
4. Replay 2026-09-21 09:30 NY (15m bar starts) and 09:45 NY (bar closes); look for confirmation text matching CLOSE, not origin. No guaranteed match to the earlier C6 Bandz result.
5. Compare **2026-10-08**, **2026-10-16**, **2026-10-22**: independently note regular CISD, `PB?`, Cephxs thick/thin line and missed cases. Capture 1 bar before event, confirmation bar, +1 and +4 bars (both positive and negative examples).
6. Disable/re-enable prototype at identical Replay endpoint, check deterministic confirmed C2/CISD labels. Do not interpret removed or evicted drawings as a past signal disappearing.
7. Report compiler errors verbatim and the **exact Pine line**. Until a successful TradingView compilation, all behavior remains **unverified**.

## Important limitations / follow-up work
- Multiple pending CISD candidates in the same direction are not maintained; a newer run can replace an old pending run.
- C2 association is a *completed* 4H sweep, not the live intrabar C2 used in some Cephxs/Po3 drawings.
- The HTF candle builder requires complete 15m segments. Missing market bars, illiquid candles or odd feed sessions can alter classification.
- The simple pending-run detector is not full swing-pivot tracking and PB? zone qualification is a single-parent approximation. Don't infer profitability or Cephxs-equivalence.
- The midpoint measurement uses the final opposing run candle: this is *not yet* a validated PB candle identifier.
- One-minute or other chart timeframes are intentionally outside this first release; 1/5/9 refers to New York 4H boundary hours, **not** a claim that 1h/5h/9h are execution timeframes.
- Next improvements only after compilation and observations: freeze event IDs, multiple pending candidates, parent-zone registry, later 16/32-bar outcomes, C2-live vs C2-closed classification and optional FVG/displacement tags.

### Change-management
This research branch is stacked on the **draft** PB specification branch rather than main. Do not merge to main or our existing working Bandz code until tests and review. The new standalone experimental script has its own name/path and cannot modify `Bandz_Po3_Profiler.pine`.
