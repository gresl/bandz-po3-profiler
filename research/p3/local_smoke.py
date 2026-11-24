"""Root-only, loopback staging smoke. Never prints token or sends trades.

Creates a distinct synthetic source, disables it in finally, retains evidence.
"""
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
token = secrets.token_hex(32)
digest = hashlib.sha256(token.encode()).hexdigest()
name = "local-smoke-" + secrets.token_hex(6)


def sql(command):
    p = subprocess.run(["runuser", "-u", "postgres", "--", "psql",
                        "-XAt", "-v", "ON_ERROR_STOP=1", "-d", "po3journal"],
                       input=command, text=True, capture_output=True, check=True)
    return p.stdout.strip()


def post(obj, key=token):
    req = Request("http://127.0.0.1:8081/bandz-hook/" + key,
                  data=json.dumps(obj).encode(), method="POST",
                  headers={"Content-Type": "application/json"})
    started = time.monotonic()
    try:
        with urlopen(req, timeout=3) as r:
            code, body = r.status, json.load(r)
    except HTTPError as r:
        code, body = r.code, json.load(r)
    print("HTTP", code, body, "elapsed_ms", round((time.monotonic()-started)*1000))
    return code, body


def main():
    b = json.loads((ROOT / "fixtures/nov23_native_preview.jsonl").read_text().splitlines()[1])
    now = int(time.time() * 1000)
    close = now // 900000 * 900000
    delta = close - b["bar_close_ms"]
    stamps = {b["bar_close_ms"]}
    for e in b["events"]:
        stamps.update(e[k] for k in ("observed_ms","c2_start_ms","cisd_close_ms","origin_open_ms")
                      if e[k] is not None)
    shift = {str(t): str(t+delta) for t in stamps}

    def move(v):
        if isinstance(v, dict):
            return {k: move(x) for k, x in v.items()}
        if isinstance(v, list):
            return [move(x) for x in v]
        if isinstance(v, int) and str(v) in shift:
            return int(shift[str(v)])
        if isinstance(v, str):
            # Reconstruct timestamp fields embedded in pipe-delimited IDs.
            return "|".join(shift.get(x, x) for x in v.split("|"))
        return v

    b = move(b)
    sid = int(sql(f"""INSERT INTO bandz_ingest.sources
       (source_name,symbol,chart_tf,anchor_tf,engine,price_places,token_sha256,enabled)
       VALUES ('{name}','FOREXCOM:GBPUSD','15','240','V2',5,decode('{digest}','hex'),true)
       RETURNING id;""").splitlines()[0])
    print("Synthetic source ID:", sid, "name:", name)
    try:
        code, result = post(b)
        assert code == 200 and result["inserted"] == 2 and result["duplicates"] == 0
        code, result = post(b)
        assert code == 200 and result["inserted"] == 0 and result["duplicates"] == 2
        b["events"][1]["reason"] = "SMOKE_CONFLICT"
        assert post(b)[0] == 409
        assert post(b, secrets.token_hex(32))[0] == 404
        counts = sql(f"""SELECT
          (SELECT count(*) FROM bandz_ingest.events WHERE source_id={sid}),
          (SELECT count(*) FROM bandz_ingest.deliveries WHERE source_id={sid}),
          (SELECT count(*) FROM bandz_ingest.delivery_events WHERE source_id={sid}),
          (SELECT count(*) FROM bandz_ingest.deliveries WHERE source_id={sid} AND status='conflict');""")
        assert counts == "2|3|4|1", counts
        print("PASS: events|deliveries|associations|conflicts =", counts)
    finally:
        sql(f"UPDATE bandz_ingest.sources SET enabled=false WHERE id={sid};")
        print("Synthetic source disabled.")


if __name__ == "__main__":
    main()
