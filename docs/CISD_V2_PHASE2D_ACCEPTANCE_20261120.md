# Phase 2D — TradingView Essential historical Pine Logs acceptance (2026-11-20)

## Acceptance verdict: PASS (bounded Bandz event collection)

The user successfully compiled the Phase 2D Pine v6 script on TradingView Essential after correcting the two `input.time(timestamp())` defaults (committed in the same branch), enabled 4F logging, and exported a **native Pine Logs CSV** with `Date,Message` columns on 2026-11-20. Original export was provided privately, **not committed** to GitHub because it contains an internal opaque Replay feed identifier.

**Feed:** replay-wrapped `FOREXCOM:GBPUSD`, 15-minute OHLC. The source's `syminfo.tickerid` was serialized in the Pine log as `={"replay":"...","symbol":"FOREXCOM:GBPUSD"}`; the Python collector now parses the CSV correctly and normalizes this to `FOREXCOM:GBPUSD`, without relying on the Replay identifier.

**Window:** close UTC `2026-11-17 00:00` through `2026-11-18 09:45`, both inclusive. Log `Date` identifies the bar open, 15 minutes before the embedded `close_ms`. All 69 checked rows had exactly this 15-minute relation; no duplicates found among 30 confirmations.

### Records

| Category | Count |
|---|---:|
| All log rows | **69** |
| Legacy CONFIRM | **13** |
| V2 CONFIRM | **17** |
| V2 LIFECYCLE | **39** |
| Lifecycle PIVOT_BREACH | 19 |
| Lifecycle INVALID_AFTER_CONFIRM | 17 |
| Lifecycle SUPERSEDED | 3 |

Lifecycle changes are **not** new confirmations. The individual V2 states/reasons remain separately inspectable in normalized reports. These are candidate events, not trade outcomes.

### 4C window reproduced exactly

Restricting confirmed close times to **Nov 17 10:30 through Nov 18 10:45 UTC**, the offline comparison returned:

| Classification | Screenshot 4C | Parsed raw logs |
|---|---:|---:|
| EXACT | 5 | 5 |
| V2_ONLY | 5 | 5 |
| LEGACY_ONLY | 2 | 2 |
| TIME_DIFF | 1 | 1 |
| LEVEL_DIFF | 0 | 0 |

The resulting 13 comparison rows represent **19 actual confirmations** (paired matches counted twice). Their UTC timestamps, direction and levels reproduce the previously recorded [eight disagreement cases](../research/fixtures/GBPUSD_20261119_4C_WINDOW_DISAGREEMENTS.csv).

### Full exported window beyond 4C cutoff

The full 30 confirmations produce **20 classified rows**:

- 8 EXACT
- 7 V2_ONLY
- 3 LEGACY_ONLY
- 1 TIME_DIFF
- 1 LEVEL_DIFF

Canonical frozen table: [full-period comparison fixture](../research/fixtures/GBPUSD_FOREXCOM_20261117_18_PINE_LOGS_FULL_COMPARISON.csv).

**Additional informative case outside 4C window:** Nov 17 **07:45 UTC**, both BEAR same candle, legacy reference `1.31926`, V2 reference `1.31911`, a **15-tick** difference (`0.00015`, 1.5 standard GBPUSD pips). This is a structural reference-selection discrepancy to examine later.

**Timing discrepancy verified:** Nov 18 BEAR legacy `07:15 UTC` vs V2 `07:30 UTC`, same `1.31889` level, 15 minutes late in V2. Late confirmation is a quality concern regardless of signal count.

**Important caution on lifecycle inference:** On Nov 17 `20:00 UTC`, the LEGACY_ONLY confirmation is **BEAR `1.32184`**, but the V2 `PIVOT_BREACH` lifecycle record at the same close is **BULL `1.32262`** (pivot bar 11700). This V2 rejection does **not** explain the bearish legacy-only event. A nearby rejection row is not causal proof. The 4C notes were explicitly labeled non-proof; this log resolves the directional mismatch.

## Operational outcome

Phase 2D **collection acceptance is complete**:
- native TradingView Pine v6 compiles,
- historical Pine Logs generate machine-readable events on Essential,
- the user can export the native CSV,
- raw CSV is parsed with UTC candle close timestamps,
- the offline result reproduces the prior 4C screenshot exactly,
- GitHub Python regression CI passed.

The parent 4E CSV-plot export may remain as an unmerged alternative, but is not required on Essential.

**Freeze this stage.** No further Replay screenshots are needed to test logging. Keep Pine Logs OFF on everyday trading templates (opt-in research exporter). The new research goal is candidate quality: assess V2's late 07:30 confirmation, 07:45 different-level confirmation, and genuine V2-only/legacy-only cases against Cephxs and independently labeled price structures; apply V2C algorithm changes only after cause analysis.

**Limitations:** This comparison does not include a machine-readable Cephxs event feed; internal agreement counts cannot be called Cephxs accuracy. MT5/FTMO candles can be supplementary but not asserted to match FOREXCOM prices exactly.
