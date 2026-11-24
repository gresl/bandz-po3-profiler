"""Real PostgreSQL integration tests. Run ONLY against disposable CI database."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import psycopg

P3 = Path(__file__).resolve().parents[1] / "p3"
sys.path.insert(0, str(P3))
from storage import ingest
from receiver import make_app

DSN = os.environ.get("BANDZ_TEST_DSN")
ADMIN = os.environ.get("BANDZ_TEST_ADMIN_DSN")
TOKEN = "a" * 64
OTHER = "b" * 64
BATCHES = [json.loads(x) for x in (P3 / "fixtures/nov23_native_preview.jsonl").read_text().splitlines()]
QUALIFIED, BOTH = BATCHES


def wire(b):
    return json.dumps(b).encode()


@unittest.skipUnless(DSN and ADMIN, "disposable PostgreSQL CI only")
class TestStorage(unittest.TestCase):
    def setUp(self):
        with psycopg.connect(ADMIN) as c:
            # Explicit guard against accidentally running against production.
            if c.execute("SELECT current_database()").fetchone()[0] != "bandz_ci":
                raise RuntimeError("refuse non-CI database")
            c.execute("TRUNCATE bandz_ingest.delivery_events, bandz_ingest.events, "
                      "bandz_ingest.deliveries, bandz_ingest.sources RESTART IDENTITY")
            for name, token in (("test", TOKEN), ("other", OTHER)):
                c.execute("""INSERT INTO bandz_ingest.sources
                    (source_name,symbol,chart_tf,anchor_tf,engine,price_places,token_sha256,enabled)
                    VALUES (%s,'FOREXCOM:GBPUSD','15','240','V2',5,%s,true)""",
                    (name, sha256(token.encode()).digest()))

    def send(self, b, token=TOKEN, now=None):
        return ingest(DSN, token, wire(b), now_ms=b["bar_close_ms"] if now is None else now)

    def count(self, table):
        with psycopg.connect(ADMIN) as c:
            return c.execute(f"SELECT count(*) FROM bandz_ingest.{table}").fetchone()[0]

    def test_duplicate_delivery_and_source_namespace(self):
        self.assertEqual(self.send(BOTH)[1]["inserted"], 2)
        self.assertEqual(self.send(BOTH)[1]["duplicates"], 2)
        self.assertEqual(self.count("events"), 2)
        self.assertEqual(self.count("deliveries"), 2)
        self.assertEqual(self.count("delivery_events"), 4)
        self.assertEqual(self.send(BOTH, OTHER)[1]["inserted"], 2)
        self.assertEqual(self.count("events"), 4)

    def test_conflict_rolls_back_entire_batch(self):
        # Seed only the link, then submit raw + altered existing link.
        b = json.loads(wire(BOTH))
        b["events"] = [b["events"][1]]
        b["event_count"] = 1
        self.assertEqual(self.send(b)[0], 200)
        b = json.loads(wire(BOTH))
        b["events"][1]["reason"] = "ALTERED"
        # Raw sorts after link in lexical order, so create a second
        # independent conflict test with raw seeded below.
        self.assertEqual(self.send(b)[0], 409)
        self.assertEqual(self.count("events"), 1)
        self.assertEqual(self.count("delivery_events"), 1)
        self.assertEqual(self.count("deliveries"), 2)
        # Seed raw for a different source: link sorts first, then conflicts.
        b = json.loads(wire(BOTH))
        b["events"] = [b["events"][0]]
        b["event_count"] = 1
        self.assertEqual(self.send(b, OTHER)[0], 200)
        b = json.loads(wire(BOTH))
        b["events"][0]["reason"] = "ALTERED"
        self.assertEqual(self.send(b, OTHER)[0], 409)
        self.assertEqual(self.count("events"), 2)
        self.assertEqual(self.count("delivery_events"), 2)
        with psycopg.connect(ADMIN) as c:
            self.assertEqual(c.execute("SELECT count(*) FROM bandz_ingest.deliveries WHERE status='conflict'").fetchone()[0], 2)

    def test_concurrent_duplicates(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: self.send(BOTH), range(4)))
        self.assertEqual([x[0] for x in results], [200]*4)
        self.assertEqual(sum(x[1]["inserted"] for x in results), 2)
        self.assertEqual(sum(x[1]["duplicates"] for x in results), 6)
        self.assertEqual(self.count("events"), 2)
        self.assertEqual(self.count("delivery_events"), 8)

    def test_auth_stale_invalid_diagnostic(self):
        self.assertEqual(self.send(BOTH, "c"*64)[0], 404)
        self.assertEqual(self.count("deliveries"), 0)
        self.assertEqual(self.send(BOTH, now=BOTH["bar_close_ms"]+900001)[0], 422)
        self.assertEqual(self.send(BOTH, now=BOTH["bar_close_ms"]-60001)[0], 422)
        self.assertEqual(ingest(DSN,TOKEN,b"{}")[0], 422)
        b = dict(BOTH, events=[], event_count=0, omitted_count=1)
        self.assertEqual(self.send(b)[1]["omitted_count"], 1)
        self.assertEqual(self.count("events"), 0)
        self.assertEqual(self.count("deliveries"), 4)
        with psycopg.connect(ADMIN) as c:
            c.execute("UPDATE bandz_ingest.sources SET enabled=false")
        self.assertEqual(self.send(BOTH)[0], 404)

    def test_qualified_and_grants(self):
        self.assertEqual(self.send(QUALIFIED)[1]["inserted"], 1)
        with psycopg.connect(DSN) as c:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                c.execute("DELETE FROM bandz_ingest.events")
        with psycopg.connect(DSN) as c:
            with self.assertRaises(psycopg.errors.InsufficientPrivilege):
                c.execute("SELECT * FROM public.production_guard")


def request(path, body, headers=None, method="POST"):
    async def run():
        messages = []
        async def recv():
            return {"type":"http.request", "body":body, "more_body":False}
        async def send(msg):
            messages.append(msg)
        await make_app("unused")({"type":"http","path":path,"method":method,
                                  "headers": headers if headers is not None else
                                  [(b"content-type",b"application/json")]}, recv, send)
        return messages[0]["status"], json.loads(messages[1]["body"])
    return asyncio.run(run())


class TestHTTP(unittest.TestCase):
    def test_boundary_checks(self):
        path = "/bandz-hook/" + TOKEN
        with patch("receiver.ingest") as db:
            self.assertEqual(request("/bad", b"{}")[0], 404)
            self.assertEqual(request(path, b"{}", method="GET")[0], 405)
            self.assertEqual(request(path, b"{}", headers=[])[0], 415)
            self.assertEqual(request(path, b"x"*40961)[0], 413)
            self.assertEqual(request(path, b"")[0], 400)
            db.assert_not_called()

    def test_commit_response_and_error(self):
        path = "/bandz-hook/" + TOKEN
        with patch("receiver.ingest", return_value=(200, {"status":"accepted"})) as db:
            self.assertEqual(request(path,b"{}")[0],200)
            db.assert_called_once_with("unused",TOKEN,b"{}")
        with patch("receiver.ingest", side_effect=RuntimeError("secret")):
            self.assertEqual(request(path,b"{}"),(503,{"status":"unavailable"}))


if __name__ == "__main__":
    unittest.main()
