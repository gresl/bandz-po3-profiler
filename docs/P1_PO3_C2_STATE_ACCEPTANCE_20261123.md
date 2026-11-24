# P1B — Po3 / C2 lifecycle event verification (24 November 2026)

This revision supersedes the initial P1 audit procedure. The original clean
`Bandz_Po3_V2_Visual_Test.pine` is unchanged. The P1 script is still a separate,
opt-in, read-only audit build; no live alerts or trade execution.

## Motivation and evidence

| GBPUSD 15m / 4H C2 | C2 start UTC | First observed | CISD close | C2 close | Prior P1 result |
|---|---|---|---|---|---|
| Nov 23 2026, bearish | 06:00 | 06:15 | 09:15 | 10:00 | CLOSED PASS / CISD_RECLAIMED |
| Sep 4 2026, bearish | 05:00 | 06:15 | 08:00 | 09:00 | CLOSED PASS / CISD_RECLAIMED |

Both are user-provided Replay observations. Neither screenshot determines the
exact reclaim close or establishes a positive qualified event. Do not invent
that timestamp. V2 is the selected raw chart detector (Cephxs-referenced,
independently developed pivot/stretch engine), whereas the original Bandz Po3
sequence adapter and close-back-through rule manage the attached CISD.

P1A erased provisional-link fields on clearing and hid earlier evidence behind
a single status. P1B keeps a separate bounded transition history.

## Event contract

All event observations are recorded only at a confirmed chart close. For
structural C2 closure the chart close must coincide with the source HTF close.
C2 identity is source candle start + side within this chart configuration.
Link matching requires side, confirmation bar, origin bar and exact level.
Timestamps shown are UTC. An origin candle is never a confirmation timestamp.

| Event | Meaning |
|---|---|
| CISD_CONFIRMED | selected raw detector confirmed; independent of C2 |
| C2_CANDIDATE | current source candle swept C1; no HTF confirmation |
| C2_CISD_LINKED_EARLY | original sequence linked a raw confirmation while C2 still forming |
| C2_CISD_LINKED_AT_CLOSE | first observed link on source closing chart bar |
| C2_CISD_LINKED_AFTER_CLOSE | first observed link later |
| C2_CONFIRMED / C2_REJECTED | observed final HTF close passes/fails strict inside-C1 condition |
| C2_CISD_QUALIFIED | structural pass, matched original live chart link, no reclaim and original visibility gates pass |
| C2_CISD_RECLAIMED | original Bandz close-back-through flag first observed, even before qualification |
| C2_CISD_LINK_ENDED | prior link cleared/replaced, original sequence inactive, C2 rejected or tracking lost |
| C2_SEQUENCE_ENDED | observed original sequence termination or C2 reject/unverified |
| C2_UNVERIFIED | source close was not observed |
| C2_SEQUENCE_UNTRACKED | original bounded record no longer present; not proof of price invalidation |

An early link is informational, not a qualified setup. A structural pass
survives later sequence termination in the audit. A reclaim does not erase a
prior qualification. Replacements retain old event snapshots while the summary
shows the latest link; a new link can qualify only while the original sequence
has not ended. No retroactive promotion of a reclaimed/ended link.

Reclamation is from original PoRec.cisdBrokeT (which stores candle OPEN time);
the audit stores the chart CLOSE at which the flag is first observed. A
CLOSE_BACK_THROUGH reason means the flag's candle-open time matches the current
chart bar; ORIGINAL_RECLAIM_ALREADY_SET means an earlier flag was first
observed now and the exact original close is not asserted. V2's separate raw
pivot invalidation rule is not changed or added as a new qualification filter.

## Install and one bounded Replay test

1. Update the existing **P1 audit script only** with Raw contents of
   `indicators/Bandz_Po3_P1_C2_State_Audit.pine` in PR #23.
2. Preserve the separate clean V2 indicator/layout. Use FOREXCOM:GBPUSD, 15m,
   profile on 4H, Chart CISD engine V2, Sequence CISD from Chart, UTC timezone.
   Keep previously tested detector and Po3 settings unchanged.
3. Enable **P1 → Show Po3/C2 lifecycle audit**. Default **Audit view = C2 summary**.
4. Replay Nov 23 from before 06:00 UTC (load prior 4H context) through the
   10:00 UTC C2 close and stop at the same 10:15 Replay endpoint previously
   captured. Send ONE readable screenshot of the summary.
5. At the same endpoint switch **Audit view = Event history**, without changing
   detector or profile settings. Send ONE screenshot of the latest transitions.
   If the relevant event is displaced, replay to shortly after 09:15 or 10:00.
   No search for a new positive case is required for this comparison.

Check the original observed 09:15 CISD and 10:00 C2 close; if the early link is
observed, its timestamp must be retained regardless of reclaim. Reclaim must be
logged separately at the observed chart close. Qualified must not be emitted
if reclamation precedes qualification. If a positive event appears naturally,
verify the qualification timestamp; otherwise it remains an acceptance gap.

## Bounds and remaining limitations

- 40 C2 summary records, 256 matched raw signals, 192 immutable transition rows.
  Event history displays latest 12; summary displays 3–7. Not durable storage
  across script recalculation or reload. Event history is regenerated on input
  changes/replay. This is not an alert/webhook payload implementation.
- Original record cache is bounded; evictions are explicitly distinguished
  from invalidation. Summary displays the latest link, not every former link.
- Chart sequence slot only for qualification. Lower-timeframe 3m/5m slots
  remain original Legacy where actually selected on a smaller chart.
- The original visibility gate remains an intentional conservative condition
  for qualified events; it is not proof of T-Spot entry eligibility or edge.
- Native Pine compile and Replay of revision B remain required.
- CI includes static source/invariant checks and 11 synthetic lifecycle
  fixtures; these do not execute Pine.
- P2 raw/early notification prototype may be developed separately after
  native verification, but qualified alerts remain gated on a positive
  qualification case, correct invalidation behavior and realtime delivery checks.
