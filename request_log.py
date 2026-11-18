"""
One JSON line per /ask request.

Written to logs/requests.jsonl and printed to stdout. Render's free tier
has no disk that survives a restart, so stdout (Render's log viewer) is
the copy that lasts. The file is for running it locally.
"""

import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_FILE = LOG_DIR / "requests.jsonl"
ANSWER_MAX = 200  # long answers get cut so one record stays one readable line


def new_request_id() -> str:
    return uuid.uuid4().hex[:8]


def write_record(
    request_id, question, status, started, tokens_before, tokens_after,
    answer=None, sources=None, best_distance=None, error=None,
):
    """status is one of: answered, refused, bad_input, error."""
    if answer and len(answer) > ANSWER_MAX:
        answer = answer[:ANSWER_MAX] + "..."

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "request_id": request_id,
        "question": question,
        "status": status,
        "answer": answer,
        "sources": sources or [],
        "best_distance": best_distance,
        "duration_ms": round((time.perf_counter() - started) * 1000),
        "prompt_tokens": tokens_after["prompt"] - tokens_before["prompt"],
        "output_tokens": tokens_after["output"] - tokens_before["output"],
        "error": error,
    }
    line = json.dumps(record, ensure_ascii=False)

    print(line, file=sys.stdout, flush=True)
    try:
        LOG_DIR.mkdir(exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass  # the stdout copy is the one that counts on Render
    return record
