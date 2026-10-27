# Po3 Alert Lifecycle Reference — GBPUSD, 2026-10-22 07:15–10:15 UTC

**Evidence class:** USER-OBSERVED, read-only PostgreSQL extraction, 14 retained webhook deliveries (IDs 860–884, noncontiguous). **No Pine modification.**
**Environment:** `FOREXCOM:GBPUSD`, chart `tf=15`, payload `htf=4H`. Alert configuration for this historical alert must be retrieved independently; do not infer that later chart Inputs were the alert snapshot.
**Primary published contract:** https://fstarlabs.com/docs/po3
**Source limitation:** Original text-plus-JSON bodies were parsed into fields; values here are *not* the full raw payload. Source `t` and `received_at` are distinct.

## Event chronology (UTC)

| ID | Event | Direction | phase / seq | entry | c1 | c2 | c3mid | dual | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| 860 | side_kill | bear | C3 / xC2 | 1.33982 | 1.33987 | 1.33831 | null | true | bear side killed |
| 861 | multi_level | bull | C3 / C3 Phase | 1.34034 | 1.33895 | 1.33831 | null | false | 4H C2 Confirmed → 15m CISD |
| 862 | xc2 | bear | C3 / xC2 | 1.33982 | 1.33987 | 1.33831 | null | true | bear side failed |
| 863 | seq_invalidated | bear | None / C3 Phase | 1.33982 | 1.33987 | 1.33831 | null | false | bear two-sided sequence invalidated |
| 864 | cisd | bull | C3 / C3 Phase | 1.34034 | 1.33895 | 1.33831 | null | false | bullish CISD confirmed |
| 867 | smt | bull | C3 / C3 Phase | 1.34034 | 1.33895 | 1.33831 | null | false | bullish SMT active |
| 871 | cisd | bull | C3 / C3 Phase | 1.34073 | 1.33895 | 1.33831 | null | false | bullish CISD confirmed |
| 873 | multi_level | bull | C3 / C3 Phase | 1.34073 | 1.33895 | 1.33831 | null | false | second bullish Gate-qualified event |
| 875 | c3_confirmed | bull | C4 / C4 Phase | 1.34073 | 1.33895 | 1.33831 | 1.34071 | false | C3 confirmed at 09:15, poststate C4 |
| 877 | smt | bull | C4 / C4 Phase | 1.34073 | 1.33895 | 1.33831 | 1.34071 | false | bullish SMT active |
| 879 | silent_close | bull | C4 / C4 Phase | 1.34073 | 1.33895 | 1.33831 | 1.34071 | false | C4 traded through C3 counter side |
| 880 | cisd | bear | C4 / C4 Phase | 1.34030 | 1.33987 | 1.33831 | 1.34071 | false | bearish CISD confirmed |
| 883 | full_kill | bull | None / C4 Phase | 1.34030 | 1.33950 | 1.33831 | 1.34071 | false | bull side killed |
| 884 | seq_invalidated | na | None / No Phase | 1.34030 | null | 1.33831 | null | false | sequence invalidated |

Sources' `t` timestamps, distinct from receiver times:
- 07:15: events 860–864 share `2026-10-22 07:15:00.324 UTC`, irrespective of receipt order.
- 08:08 SMT: `08:08:21.011 UTC` (intrabar).
- 08:30 CISD & Multi-Level: `08:30:00.605 UTC`.
- 09:15 C3 confirmed: `09:15:00.537 UTC`.
- 09:45 SMT: `09:45:21.010 UTC`.
- 10:00 silent_close & opposing CISD: `10:00:00.614 UTC`.
- 10:15 full_kill & seq_invalidated: `10:15:00.523 UTC`.

Structural levels:
- `c2=1.33831`, `c2h=1.34085`, `c2l=1.33831` remain the same across all 14 events. This is **a stable observed level snapshot**, not proof of a unique global sequence ID.
- `htfopen` is 1.33980 through 08:30 and 1.34073 from 09:15 onwards (higher-timeframe context changed).
- `c3mid` becomes 1.34071 at 09:15 (first C3 complete), retained at 10:00/10:15 except final sequence invalidated where it is null.
- `entry` at 10:15 equals the latest bearish CISD (1.34030) even though full_kill direction is bullish. This is **expected**: published contract says entry means LAST confirmed chart CISD, including on non-CISD events; it is not an event-specific order entry or sequence ID.
- `c1` is directional at the instant of emission, and null for dir=na. It shifts with the interpretation / active side. No assumption of immutable `c1` across different event directions.
- `dual=true` in bearish side_kill is expected under published contract: event observes two-sided state when emitted, not a guaranteed post-kill snapshot.

## Observed and inferred; never conflate

**Observed:** Five different `evt` keys share the exact same source `t` at 07:15. Opposing directions and different `seq`/dual states coexist as emitted records. Two separate bullish Gate events at 07:15 and 08:30 with distinct entry references; the second does not require (as observed) a newly visible C2 between them. `c3_confirmed` reports `C4 Phase`. `silent_close` and `full_kill` occur at distinct close boundaries, separated by 15 minutes, and raw bearish CISD confirms between them.

**Source-documented:** `multi_level` is Gate-qualified Lazy-mode entry; `cisd` raw feed bypasses Gate; `entry` is last chart CISD; `seq` and `dual` are instantaneous state; lifecycle keys differ; close-based confirmation as documented. The webhook `t` is event-fire time, not proof of actual candle close. The user’s historical TV alert instance settings are not currently verified.

**Hypotheses needing cross-sample tests:**
1. The HTF engine keeps *direction-specific* branches and later collapses to a single side. UI may hide one side even while raw lifecycle events describe it.
2. Repeated `multi_level` events may be triggered by *new qualifying CISDs* on separate chart closes within the same HTF phase.
3. `silent_close` is a C4 continuation/counter-side test, not the same as full sequence invalidation.
4. `c3_confirmed` reporting `phase=C4` represents post-transition state on event emission, not a timestamp error.
These must not be implemented as universal logic without more cases or rules.

## Minimum reproducer for our research state machine (when implemented)

1. Preserve exact raw payload, received timestamp, source alert-instance/config ID, webhook source symbol and payload `tkr` separately. Include `t`, `evt`, `dir`, `seq`, `dual`, `phase`, all prices, and receipt latency; do not discard null.
2. Store each event, including the five events with **identical `t` at 07:15**. Dedup cannot key only on symbol/time/candle; include `evt`, `dir`, `tf`, `t`, and alert instance; record repeats, ambiguous matches, and payload hashes.
3. Track **raw structure versus entry qualification** as separate streams: `cisd` vs `multi_level`, with provisional `smt`/sweep and confirmed chart CISD separated.
4. Treat `c1`, `c2`, `entry`, `htfopen` as event-time references, **not stable sequence IDs**.
5. Represent `side_kill`, `xc2`, `silent_close`, `full_kill`, `seq_invalidated` as distinct event types. Do not derive internal ordering from webhook receipt order when source timestamp is equal.
6. Regression should reproduce observable **event set and causal time** before striving for exact payload order. No alerts/execution on provisional data without confirmation.

## Time-limited follow-up

With Cephxs access potentially ending 2026-10-31, prioritize collecting `seed`/two-sided births, `arm` and `promote`, `c2_confirmed`, `early_bird_wait/final` if enabled, in already stored data. Avoid endless replay toggles and PB validation. One additional `seed → side_kill/promote/full_kill` episode and one `C3 → C4 → silent_close` contrast would be more valuable than repeated raw CISD screenshots.
