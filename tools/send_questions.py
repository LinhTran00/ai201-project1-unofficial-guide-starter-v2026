#!/usr/bin/env python3
"""
Send a fixed set of requests to a running serve.py and save what came back.

    python tools/send_questions.py http://localhost:5000 --label before
    python tools/send_questions.py https://<your-app>.onrender.com --label after

Same requests every time, so the capstone trials are repeatable:
  - GET /health first
  - the in-corpus questions from questions.py
  - the out-of-scope questions from questions.py
  - a handful of bad inputs (empty, not JSON, wrong types)

Results go to results/capstone_<label>_<timestamp>.json. Standard library
only, so it runs anywhere Python does.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from questions import OUT_OF_SCOPE, answered  # noqa: E402

TIMEOUT = 180  # a Render free instance waking from sleep can take a while

# (name, raw request body). Sent as-is, with a JSON content type.
BAD_INPUTS = [
    ("empty question", '{"question": ""}'),
    ("missing question key", '{"q": "hello"}'),
    ("not json", "this is not json"),
    ("question is a number", '{"question": 5}'),
    ("body is a list", '["hi"]'),
]


def send(method, url, body=None):
    data = body.encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")

    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            status, text = resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        status, text = exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001 — a timeout is a result too
        status, text = None, f"{type(exc).__name__}: {exc}"
    elapsed_ms = round((time.perf_counter() - started) * 1000)

    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        parsed = None
    return {"status_code": status, "client_ms": elapsed_ms,
            "json": parsed, "text": None if parsed is not None else text[:500]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="base URL, e.g. http://localhost:5000")
    parser.add_argument("--label", default="run")
    args = parser.parse_args()
    base = args.url.rstrip("/")

    requests_to_send = (
        [("in_corpus", q["question"], json.dumps({"question": q["question"]}))
         for q in answered()]
        + [("out_of_scope", q, json.dumps({"question": q})) for q in OUT_OF_SCOPE]
        + [("bad_input", name, body) for name, body in BAD_INPUTS]
    )

    print(f"GET {base}/health")
    health = send("GET", f"{base}/health")
    print(f"  {health['status_code']}  {health['client_ms']} ms  {health['json']}")

    rows = []
    for kind, name, body in requests_to_send:
        result = send("POST", f"{base}/ask", body)
        reply = result["json"] or {}
        rows.append({"kind": kind, "name": name, "body": body, **result})
        tag = ("refused" if reply.get("refused") else "answered") if "answer" in reply else "-"
        print(f"  {result['status_code']}  {result['client_ms']:>6} ms  "
              f"{kind:<12} {tag:<8} {name[:60]}")

    out_dir = ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    out = out_dir / f"capstone_{args.label}_{stamp}.json"
    out.write_text(json.dumps(
        {"url": base, "label": args.label, "sent_at": stamp,
         "health": health, "requests": rows},
        indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {len(rows)} requests to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
