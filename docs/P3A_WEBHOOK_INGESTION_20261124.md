# P3A — isolated Bandz webhook ingestion (24 November 2026)

Status: offline contract/decoder and schema proposal, not deployed. Preserve
existing production /opt/po3-journal, nginx /hook/<token>, worker and existing
po3journal tables. No changes to LuxAlgo trade journal or trade execution.
Existing deployment details are from earlier project records; current host
configuration must be inspected before writing a migration.

## Decisions
- Keep existing bandz.po3.p2a.v1 schema for both P2A and P2B; qualification
  is additive. Validate exact source symbol, chart_tf, anchor_tf, engine,
  tick precision, known event types, counts, timestamp chronology and
  reconstructed identities. Raw prices use Decimal, not float.
- Source scoped identity: (source_id, event_id) unique. One source per
  configured alert instance/profile. Multiple registered profiles remain
  separately traceable; cross-source aggregation can be done at query time.
- New isolated endpoint proposed: /bandz-hook/<high-entropy-token>.
  Authenticate registered token via SHA-256 digest; disabled by default;
  do not log token or include it in response. Apply TLS, bounded body,
  rate limit, least-privilege database user and a live freshness policy
  (future tolerance, maximum age) after checking provider requirements.
  Do not expose a Preview import through the public route.
- Retain exact authenticated request bytes and digest in delivery table.
  Do not persist unauthorized traffic. Cap request size before reading.
  Persist malformed/conflicting authenticated deliveries with error code,
  but never insert partial events from them.
- For valid live batches use one transaction. Insert delivery, then each
  event in stable event_id order with INSERT ... ON CONFLICT DO NOTHING.
  For existing identity compare stored event_json and bar_close_price;
  identical => duplicate delivery association, unequal => conflict.
  Roll back all new events/associations for a conflict (savepoint), retain
  conflict delivery status. Commit before ACK. Handle DB errors with 5xx.
  No silent overwrite of original event. No promise of provider retry.
- Preserve omitted_count and invalid_identity_count even for zero-event
  diagnostics. These are data-quality incidents, not valid trade signals.
- Schema SQL is a proposal, not a production migration. No DB credentials,
  service installation, nginx edits, grants, retention or deployment yet.

## Gates
1. Offline strict decoder and fixture tests.
2. Inspect current service/worker layout and database schema read-only.
3. Implement transactional repository + HTTP handler + PostgreSQL
   concurrency, duplicate, collision, rollback, auth and size tests.
4. Deploy isolated staging service and route; no existing alerts redirected.
5. Live P2B qualified and follow-up delivery smoke test. Enable Bandz
   staging webhook only after receiver validation and deliberate approval.
6. Compare Bandz and Cephxs records using separate sources; integrate
   journal views later. No automatic entries.

Open: P1A/P1B timing discrepancy; Preview duplicate cause; P2B live
qualification/follow-up verification; actual host wiring; cross-profile
version namespace; receiver durability/concurrency and alert expiry policy.
