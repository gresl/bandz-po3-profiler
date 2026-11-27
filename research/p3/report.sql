-- Bandz P3D: read-only research report; no schema changes.
-- Run as an authorized journal reader, not the ingestion application.
-- Excludes synthetic sources. All timestamps shown in UTC.
BEGIN READ ONLY;
SET LOCAL TIME ZONE 'UTC';
SET LOCAL statement_timeout = '5s';

\echo === Real source delivery health ===
WITH d AS (
    SELECT source_id, count(*) AS deliveries,
           count(*) FILTER (WHERE status='accepted') AS accepted,
           count(*) FILTER (WHERE status='invalid') AS invalid,
           count(*) FILTER (WHERE status='stale') AS stale,
           count(*) FILTER (WHERE status='conflict') AS conflicts,
           coalesce(sum(omitted_count),0) AS omitted,
           coalesce(sum(invalid_identity_count),0) AS invalid_identity,
           max(received_at) AS last_delivery
    FROM bandz_ingest.deliveries GROUP BY source_id
), e AS (
    SELECT source_id, count(*) AS unique_events,
           min(observed_ms) AS first_ms, max(observed_ms) AS last_ms
    FROM bandz_ingest.events GROUP BY source_id
), a AS (
    SELECT source_id, count(*) AS associations
    FROM bandz_ingest.delivery_events GROUP BY source_id
)
SELECT s.id AS source_id, s.source_name, s.enabled,
       coalesce(d.deliveries,0) AS deliveries,
       coalesce(d.accepted,0) AS accepted,
       coalesce(d.invalid,0) AS invalid,
       coalesce(d.stale,0) AS stale,
       coalesce(d.conflicts,0) AS conflicts,
       coalesce(d.omitted,0) AS omitted,
       coalesce(d.invalid_identity,0) AS invalid_identity,
       coalesce(e.unique_events,0) AS unique_events,
       coalesce(a.associations,0)-coalesce(e.unique_events,0) AS duplicate_associations,
       d.last_delivery, to_timestamp(e.first_ms/1000.0) AS first_event_utc,
       to_timestamp(e.last_ms/1000.0) AS last_event_utc
FROM bandz_ingest.sources s
LEFT JOIN d ON d.source_id=s.id
LEFT JOIN e ON e.source_id=s.id
LEFT JOIN a ON a.source_id=s.id
WHERE s.source_name NOT LIKE 'local-smoke-%'
ORDER BY s.id;

\echo === Event counts by source and type ===
SELECT s.source_name,e.kind,e.side,count(*) AS observed_events
FROM bandz_ingest.events e
JOIN bandz_ingest.sources s ON s.id=e.source_id
WHERE s.source_name NOT LIKE 'local-smoke-%'
GROUP BY s.source_name,e.kind,e.side
ORDER BY s.source_name,e.kind,e.side;

\echo === Most recent observed linked lifecycles (not complete market coverage) ===
WITH links AS (
    SELECT e.source_id,e.link_id,e.c2_id,e.signal_id,e.side,
           min(e.observed_ms) FILTER (WHERE e.kind='C2_CISD_LINKED_EARLY') AS early_ms,
           min(e.observed_ms) FILTER (WHERE e.kind='C2_CISD_QUALIFIED') AS qualified_ms,
           min(e.observed_ms) FILTER (WHERE e.kind='C2_CISD_RECLAIMED') AS reclaimed_ms,
           min(e.observed_ms) FILTER (WHERE e.kind='C2_CISD_LINK_ENDED') AS ended_ms,
           max(e.observed_ms) AS last_ms
    FROM bandz_ingest.events e
    JOIN bandz_ingest.sources s ON s.id=e.source_id
    WHERE s.source_name NOT LIKE 'local-smoke-%' AND e.link_id IS NOT NULL
    GROUP BY e.source_id,e.link_id,e.c2_id,e.signal_id,e.side
), rejects AS (
    SELECT source_id,c2_id,min(observed_ms) AS rejected_ms
    FROM bandz_ingest.events
    WHERE kind='C2_REJECTED' GROUP BY source_id,c2_id
)
SELECT s.source_name,l.side,
       to_timestamp(l.early_ms/1000.0) AS early_utc,
       to_timestamp(l.qualified_ms/1000.0) AS qualified_utc,
       to_timestamp(l.reclaimed_ms/1000.0) AS reclaimed_utc,
       to_timestamp(l.ended_ms/1000.0) AS link_ended_utc,
       to_timestamp(r.rejected_ms/1000.0) AS c2_rejected_utc,
       (l.qualified_ms-l.early_ms)/60000.0 AS early_to_qualified_minutes,
       l.link_id
FROM links l
JOIN bandz_ingest.sources s ON s.id=l.source_id
LEFT JOIN rejects r ON r.source_id=l.source_id AND r.c2_id=l.c2_id
ORDER BY l.last_ms DESC,l.link_id
LIMIT 30;

\echo === Existing Cephxs journal coverage inventory (no event equivalence assumed) ===
SELECT source_id,source_ticker,chart_tf,anchor_tf,raw_event,direction,
       count(*) AS rows,
       min(source_time) AS first_utc,max(source_time) AS last_utc
FROM public.normalized_events
GROUP BY source_id,source_ticker,chart_tf,anchor_tf,raw_event,direction
ORDER BY source_id,raw_event,direction;
COMMIT;
