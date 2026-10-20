# Phase C3 — Consecutive raw CISD capture, blinded labels and fixed outcome horizons

**State:** C3 capture protocol and CSV validator. **Pine branch:** `feature/cisd-v1.4-phase-c-outcome-research` (draft PR #6); **no Pine edits in C3**. Do not merge PR #6 or change live trading defaults as a result of these records. Scope: discretionary research only, no orders, new alerts, or profitability claims.

## Freeze the cohort before evaluating outcomes

- Primary: EURUSD `FOREXCOM:EURUSD`, chart **15m**, anchor **4h**, audit time **America/New_York**, fixed symbol/feed and fixed Pine SHA. GBPUSD/xC2 is a **separate replication** cohort, not mixed into the first 30-50 cases.
- Predetermine a NY start date/time **before observing outcomes**. Record every **consecutive confirmed raw** CISD after that point until 30–50 unique raw events are collected. Count bullish, bearish, eligible, rejected, unattractive and no-trade events; do not skip a signal because the eventual result looks poor. Do not treat October 8/16 debugging examples as a randomly selected sample.
- Keep a documented settings profile (copy input values or a fixed screenshot). Choose `All + C2 highlighted`, raw/all diagnostic event capture, retained events 100, event-time audit ON, and later 16/32-bar outcomes ON. Avoid draw filters hiding unqualified raw signals. Audit offset is a **temporary selector**, not event identity. Input changes force Pine recomputation, so start a new version/cohort when inputs change.
- Freeze the manual review rubric and thresholds **before** sampling. The Phase B 55% body/range, 0.6 body/ATR14, 70% directional close hypotheses are not to be tuned on this sample. A `MATCH` panel status establishes internal consistency only.

## One continuous Replay pass (do not jump 32 bars and miss overlapping signals)

1. Step Replay one **completed** 15-minute candle at a time. On every new raw CISD confirmation, pause immediately and identify the event by feed, direction, NY *confirmation-close* timestamp, CISD level and the displayed start/confirm bars. Never use the offset or local bar index as the durable ID.
2. **Before revealing future candles:** write one CSV row with the immutable `THEN` columns (including negative/absent FVG or C2 evidence), `AT CLOSE`, and an independent manual `technical_review_label` of **valid**, **invalid**, or **uncertain** with a reason. Set `technical_review_blinded=yes` only if this was genuinely done without exposure to later bars. Otherwise record `no` and treat the record separately in validity-agreement analysis. Never invent an FVG born time or substitute its later appearance for an at-close condition.
3. Continue Replay sequentially. When new raw events occur before older events' +16 or +32 maturity, record them in their own new rows **at their confirmation time**, then continue. Earlier events remain pending; use their temporary audit offsets to revisit as needed. Avoid advancing +32 directly past unrecorded confirmations.
4. At each event's **16th and 32nd subsequent closed chart bars**, copy the corresponding LATER metrics into that *same row*. `PARTIAL`/`CENSORED`/`NOT_EVALUABLE` are not FINAL. Capture MFE, MAE, terminal ATR return and first +1/-1 ATR touch order. A same-bar opposing threshold hit is `AMBIGUOUS`, not a known favorable first hit. Do not infer actual fills or executable P&L.
5. Check the event-time panel's `THEN`/`AT CLOSE` fields remain immutable and `MATCH` persists without indicator reloading. The **first** observed 31→32 transition for a new event (no hide/show, no input edit) is a regression checkpoint. If counts or frozen flags change, pause the dataset and report the mismatch rather than retrospectively repairing rows.
6. Preserve any missed/ambiguous field as blank/`unknown` with an explicit note. Track censored horizons and reproduce chart snapshots for a small number of disagreements, not every event. A closed bar observed in Replay is not proof that there was no repainting under other feeds or configurations.

## CSV and integrity checks

Fill [`research/cisd_phase_c_sample.csv`](../research/cisd_phase_c_sample.csv) **without changing its header order**. `event_key` should encode `feed|15|240|NY-close-ISO|BULL/BEAR|level`; this key is unique within the cohort. Keep ISO timestamps with explicit NY offset when practicable, to avoid DST confusion. `source_commit_sha` and `settings_profile` pin the exact run. `unknown`/empty means not established; **never encode absence of evidence as a positive pass**. For numeric outcome values use ATR units as displayed, not pips. `technical_review_blinded` is `yes` or `no`; a historical example viewed with the outcome already known cannot be called blinded.

Run from the repository root:

```bash
python3 research/validate_cisd_sample.py
```

The checker is deliberately strict about schema, identity and numeric syntax, but reports completeness problems as warnings while a sample is still in progress. It does not generate observations, test the indicator, or guarantee that events were consecutive. The human researcher must maintain an acquisition log and verify missed signals. Keep screenshots/notes outside the CSV if their provenance is needed, with an event-key cross-reference.

## Acceptance gates for C3 to C4

- 30–50 consecutive raw CISD rows from one fixed prespecified cohort; no selective exclusions; no duplicates; records distinguish `valid`, `invalid` and `uncertain` before observing outcomes, or explicitly disclose non-blinded review.
- Fixed source SHA/settings; complete confirmed-time evidence where available; missing formation evidence flagged rather than silently passed.
- Completed 16/32 horizons for mature events; incomplete/censored histories transparently reported; no lookahead or later FVG/C2 used to revise at-close labels.
- Check one **separate** continuous 31→32 Replay transition and the GBPUSD/xC2/legacy-mode regression **before** merging Phase C; compilation alone is insufficient.
- C4 reports descriptive distributions and rejected-good/passed-bad examples, not optimized thresholds or backtested financial performance.
