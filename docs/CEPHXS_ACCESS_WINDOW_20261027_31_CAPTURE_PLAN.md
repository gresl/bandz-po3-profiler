# Cephxs Po3 Ultimate+ access window — evidence capture plan
Date: 2026-10-27; target cutoff: 2026-10-31 or earlier if vendor revokes access.
Status: research plan only, **no Pine change**, no unverified parity claim.
Branch: `experiment/cephxs-base-parity-v0.1`.

## Objective
Preserve observations that will not be available after proprietary indicator access ends. Priority order: alert stream and settings > Gate and phases > state transitions/negative controls > SMT/PSP nuances > PB. Future 1/5/9 CRT and Mado C3 materials are separate evidence layers: do not silently reinterpret Cephxs data.

## Verified sources
- FStarLabs Po3 Suite documentation: https://fstarlabs.com/docs/po3 (16 named alert conditions, 22 event types, fixed v1 JSON contract, Gate/phase timing, provisional-event caveat).
- TradingView Replay limitations: https://www.tradingview.com/support/solutions/43000474024-how-do-i-turn-bar-replay-on/ (server-side alerts operate on real-time data; cannot create new alerts in Replay).
- TradingView alert snapshot behavior: https://tradingview.com/pine-script-docs/faq/alerts/ (changing script/settings does not change a running alert).
- TradingView webhook info: https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/ (POST with JSON content type for valid JSON; securely authenticate inbound).
- TradingView script publishing rules: https://www.tradingview.com/support/solutions/43000590599-script-publishing-rules/ (responsible reuse and original work).

## Existing code inventory (checked on Oct 27)
- `Bandz_Po3_Profiler.pine` ~2,926 lines, C1–C4/T-Spots, 3 HTF lanes, PSP, SMT/SSMT, CISD, STDV, FVG, C6 audits.
- Search of source found **no `alertcondition()` or `alert()` calls**. Do not imply existing production alerting.
- Existing docs: M0 CISD [base] parity, PB-A research, C6 parity; do not overwrite or recast PB observations as confirmed PB semantics.
- Current published Cephxs JSON schema can inform *original* design; the proprietary code is not available.

## P0 — preserve settings before any more experiments
Take FULL Inputs screenshots for **Po3 [Ultimate+] AND Po3 Alert Automations**; scroll every group and capture options by opening the dropdown (one image per group as necessary). Include: chart feed, 15m, 4H profile, America/New_York chart time, directional bias, session filter, timeframe stack, Level 1/2/3 phases and sequence filters, Lazy vs Early Bird, CISD sensitivity/size/purge, SMT/PSP asset group and filters, C1-C4/xC2, T-Spot, FVG/STDV, projected HTF candle open/label and status-bar options. Record exact script title and version if shown. Export/screenshot alert Condition dropdown, including 16 named conditions and "Any alert() function call".

Also capture actual Profile on/HTF candle ladder defaults versus our Bandz inputs; distinguish visual-only settings from rule gates.

## P1 — activate live event stream (highest unique information yield)
**No assumption that current webhook.grecea.net TLS, /ingest, or auth is ready. Verify them first.** Current journal receiver may require Bearer auth whereas TradingView custom alerts do not send that header. Implement/test a separate secured path-token endpoint on HTTPS, restrict to genuine TradingView IPs when practical, ensure secrets excluded from logs, and keep ingest-only (no orders).

Po3 Alert Automations:
- Use `Webhook Payload = JSON only`; select `Any alert() function call`; webhook URL = validated secret-path endpoint; normal/live market chart, not Replay; active/open-ended if plan supports.
- Freeze one baseline profile: `FOREXCOM:EURUSD`, chart TF 15m, anchor 4H, chart timezone America/New_York, bias Auto. Capture every setting before creation; profile should be as broad as sensible for RAW feeds, but don't silently loosen the Gate for comparisons.
- If capacity permits, second baseline `FOREXCOM:GBPUSD` (or AUDUSD) using same setup, rather than multiplying settings variants.
- Alerts are server-side snapshots; changes to indicator settings or source require a *new* alert. Name alerts with feed+TF+HTF+profile revision.
- Vendor access expiration may disable the script or alert: do NOT rely on continuation after cutoff. Export alert log and database by Oct 31.
- Send test POST payload from controlled local client only after secure receiver is validated; verify code 2xx, raw logging, normalized row, duplicates, malformed/null fields, and no trading execution.

**Raw fields (fixed published v1 contract):** `v ind evt dir tkr tf bias htf phase px entry c1 c2 c2h c2l c3mid htfopen t msg dual seq`.
**Events:** entry: `early_bird_wait early_bird_final multi_level`; raw: `cisd smt c2_sweep c2_confirmed c3_confirmed c4_confirmed seq_invalidated`; HTF lifecycle: `seed side_kill full_kill promote xc2 zero_xc2 late_xc2 arm xc3 zero_xc3 late_xc3 silent_close`.
- Not Gate filtered: raw feeds; all obey session filter.
- Intrabar provisional: `early_bird_wait`, `c2_sweep`; stable close-only: final CISD/C2/C3/C4 confirmations as vendor documents; don't equate provisional event with executable confirmation.
- Timestamp `t` = event-fire Unix milliseconds; `entry` = LAST confirmed chart CISD, not necessarily attached to current event; missing values can be null.
- De-dup key provisional suggestion: chart alert instance/profile + symbol + timeframe + event + direction + timestamp, with raw-body hash and first/last receive times. Keep identical retransmissions and divergent payloads separately for audit, never silently discard raw.
- Record receipt time UTC, event timestamp UTC and NY, latency, alert instance identity, chart/HTF, exact JSON body, source config hash, and normalized state; the raw payload is authoritative.

## P2 — historical UI capture (live alerts do NOT fire on Replay)
Select 2-3 periods already known: Oct 8 bullish, Oct 22 bearish, Oct 26 NY; plus a failed C2/No Phase negative control. Under a frozen identical indicator configuration, record: C1 sweep -> C2 provisional/confirmed -> C3 Active/Confirmed -> C4 Active/Confirmed or invalidation, the exact first knowable close, C1/C2/HTF open values, sequence state text, and confidence in drawing annotation.

Use narrow screenshot packs: (A) setting / trigger definition (once), (B) first appearance or phase transition, (C) +1/+4 closed bars, (D) mismatch/negative case. Avoid unlimited 1-candle screenshot chains unless isolating an actual mismatch. Normal candle timestamps are OPEN, confirmation is CLOSE.

Compare: exact HTF boundary (America/New_York; DST-safe), profile and Gate stage, T-Spot reference and distribution, C2 sweep vs confirmed, two-sided xC2, invalidations, SMT/PSP assets and scale, optional FVG/STDVs. Tag `OBSERVED`, `DOC_DERIVED`, `INFERRED`, `UNVERIFIED`.

## P3 — research matrix
| Observation | Source | Price/time precision | Comparison / classification |
| --- | --- | --- | --- |
| Alert event | TV JSON raw | exact `t`, tick-rounded price | `MATCH`, `DIFF_EVENT`, `DIFF_CLOSE`, `UNVERIFIED` |
| State transition | Po3 Ultimate screenshot | NY candle open and inferred close until Data Window | `MATCH`, `DIFF_PHASE`, `AMBIGUOUS` |
| SMT/PSP | Po3 screenshot plus comparator symbols/settings | reference pair and first appearance | `MATCH`, `CEPHXS_ONLY`, `BANDZ_ONLY` |
| PB | prior M0 screenshots | visual only without exact rule | `CANDIDATE`, not confirmed equivalence |

## P4 — by access cutoff
Archive in your own storage (not public secrets): settings screenshots, exact versions, alert-condition dropdown, JSON payload export, TradingView Alert Log CSV if available, research capture index, 3-5 positive and 2-3 negative state examples, README with time/feed/profile, checksum list. Proprietary video/document material remains private unless author permits redistribution.
No claim that alerts will continue after access revoked.

## Next development milestones after capture
A. Add separate no-execution alert-transport module to original Bandz/Po3 engine: `alert()` dynamic structured JSON plus 4-6 essential `alertcondition()`; freeze event semantics/timing, version contract and replay tests. A separate indicator for alerts is preferred if plot budget/TV alert lifecycle warrant it.
B. Implement explicit causal Gate inputs and state transitions (HTF -> MTF -> chart CISD), confirmed / provisional split, session windows and informative rejections; no backdated signals.
C. Validate event-by-event against the captured Cephxs stream; report mismatches and unknowns, not simulated accuracy.
D. Separate CRT 1/5/9 and Mado C3 research layer tagged by source, date, rule status, and test-case; protect baseline parity regression.
E. Return to original PB-A parent/revisit/departure hypothesis once alert/state evidence is preserved.

## Go / no-go
GO to algorithm changes only with: stable observation definition, source + timestamp, both positive and negative cases, original causal rule, test fixtures, and independent replay compilation. Keeping event capture operational precedes tuning geometry.
