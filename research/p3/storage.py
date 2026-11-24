"""Transactional Bandz receiver storage. PostgreSQL 16, psycopg 3.

No imports or writes to the existing public journal schema.
"""
from hashlib import sha256
import re
import time

import psycopg
from bandz_batch import decode, InvalidBatch, Source, MAX_BYTES


TOKEN = re.compile(r"[0-9a-f]{64}", re.ASCII)
MAX_AGE_MS = 15 * 60 * 1000
FUTURE_MS = 60 * 1000


class Conflict(Exception):
    pass


def ingest(dsn, token, raw, *, now_ms=None):
    """Return HTTP status and safe response, after DB commit.
    now_ms is injectable only for offline tests; HTTP never accepts it.
    """
    if not isinstance(token, str) or TOKEN.fullmatch(token) is None:
        return 404, {"status": "not_found"}
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_BYTES:
        return 413, {"status": "invalid_size"}

    token_digest = sha256(token.encode("ascii")).digest()
    digest = sha256(raw).digest()
    # Explicit outer transaction plus nested savepoint for all event writes.
    with psycopg.connect(dsn, autocommit=True, connect_timeout=2) as conn:
        with conn.transaction():
            conn.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
            conn.execute("SET LOCAL statement_timeout = '1200ms'")
            conn.execute("SET LOCAL lock_timeout = '600ms'")
            row = conn.execute("""
                SELECT id, symbol, chart_tf, anchor_tf, engine, price_places
                FROM bandz_ingest.sources
                WHERE token_sha256 = %s AND enabled
            """, (token_digest,)).fetchone()
            if row is None:
                return 404, {"status": "not_found"}
            sid, *config = row
            try:
                b = decode(raw, Source(*config))
                # PostgreSQL jsonb rejects NUL and invalid Unicode surrogates.
                # Event reasons are machine identifiers, never arbitrary text.
                if any(re.fullmatch(r"[A-Za-z0-9_ -]{1,128}", e["reason"]) is None
                       for e in b["events"]):
                    raise InvalidBatch("reason characters")
            except InvalidBatch:
                delivery = _delivery(conn, sid, raw, digest, "invalid", "INVALID_BATCH")
                return 422, {"status": "invalid", "delivery_id": delivery}

            now = time.time_ns() // 1000000 if now_ms is None else now_ms
            close = b["bar_close_ms"]
            if close < now - MAX_AGE_MS or close > now + FUTURE_MS:
                delivery = _delivery(conn, sid, raw, digest, "stale", "CLOSE_OUTSIDE_WINDOW", b)
                return 422, {"status": "stale", "delivery_id": delivery}

            delivery = _delivery(conn, sid, raw, digest, "accepted", None, b)
            inserted = duplicates = 0
            try:
                with conn.transaction():
                    # Keep Decimal prices intact: extract exact event JSON from
                    # validated original bytes in PostgreSQL, not float conversion.
                    original = raw.decode("utf-8")
                    for i, e in sorted(enumerate(b["events"]), key=lambda x: x[1]["event_id"]):
                        args = (sid, e["event_id"], delivery, e["observed_ms"], e["kind"],
                                e["side"], e["c2_id"], e["signal_id"], e["link_id"],
                                b["bar_close_price"], original, i)
                        created = conn.execute("""
                            INSERT INTO bandz_ingest.events
                            (source_id,event_id,first_delivery_id,observed_ms,kind,side,
                             c2_id,signal_id,link_id,bar_close_price,event_json)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                    (%s::jsonb -> 'events' -> %s::int))
                            ON CONFLICT (source_id,event_id) DO NOTHING
                            RETURNING event_id
                        """, args).fetchone()
                        if created:
                            inserted += 1
                        else:
                            same = conn.execute("""
                                SELECT event_json = (%s::jsonb -> 'events' -> %s::int)
                                       AND bar_close_price = %s
                                FROM bandz_ingest.events
                                WHERE source_id = %s AND event_id = %s
                            """, (original, i, b["bar_close_price"], sid, e["event_id"])).fetchone()
                            if not same or not same[0]:
                                raise Conflict()
                            duplicates += 1
                        conn.execute("""
                            INSERT INTO bandz_ingest.delivery_events
                            (source_id,delivery_id,event_id) VALUES (%s,%s,%s)
                        """, (sid, delivery, e["event_id"]))
            except Conflict:
                # Savepoint rolled back all new events and associations, but
                # the original authenticated delivery is retained for review.
                conn.execute("""
                    UPDATE bandz_ingest.deliveries
                    SET status = 'conflict', error_code = 'EVENT_ID_CONFLICT'
                    WHERE id = %s AND source_id = %s
                """, (delivery, sid))
                return 409, {"status": "conflict", "delivery_id": delivery}

            return 200, {"status": "accepted", "delivery_id": delivery,
                         "inserted": inserted, "duplicates": duplicates,
                         "omitted_count": b["omitted_count"],
                         "invalid_identity_count": b["invalid_identity_count"]}


def _delivery(conn, sid, raw, digest, status, error, b=None):
    vals = (None, None, None, None) if b is None else (
        b["bar_close_ms"], b["event_count"], b["omitted_count"], b["invalid_identity_count"])
    return conn.execute("""
        INSERT INTO bandz_ingest.deliveries
        (source_id,body,body_sha256,status,error_code,bar_close_ms,event_count,
         omitted_count,invalid_identity_count)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
    """, (sid, raw, digest, status, error, *vals)).fetchone()[0]
