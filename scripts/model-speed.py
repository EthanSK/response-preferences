#!/usr/bin/env python3
"""Report the recorded service tier of a Codex turn without printing its log body.

Pass the exact thread and turn IDs. A runner may omit the turn ID for a freshly
created, single-turn ephemeral thread when no turn ID was returned.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sqlite3
from uuid import UUID


def read_service_tier(thread_id: str, turn_id: str | None = None) -> str | None:
    if str(UUID(thread_id)) != thread_id or (turn_id and str(UUID(turn_id)) != turn_id):
        raise ValueError("Use exact Codex thread and turn IDs.")
    codex_directory = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    database = codex_directory / "logs_2.sqlite"
    try:
        with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True, timeout=0.25) as connection:
            rows = connection.execute(
                """SELECT feedback_log_body FROM logs
                   WHERE thread_id = ? AND target = 'feedback_tags'
                     AND instr(feedback_log_body, ?) > 0
                     AND instr(feedback_log_body, '"service_tier":') > 0
                   ORDER BY id DESC LIMIT 128""",
                (thread_id, turn_id or 'turn.id='),
            ).fetchall()
    except sqlite3.Error:
        return None

    evidence = set()
    for (body,) in rows:
        observed_turn = re.search(r'\bturn\.id="([0-9a-f-]{36})"', body)
        tier = re.search(r'"service_tier"\s*:\s*"([a-z][a-z0-9_-]{0,23})"', body)
        if observed_turn and tier and (turn_id is None or observed_turn.group(1) == turn_id):
            evidence.add((observed_turn.group(1), tier.group(1)))
    if len(evidence) == 1:
        return next(iter(evidence))[1]
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thread-id", required=True)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--turn-id")
    target.add_argument("--single-turn", action="store_true")
    arguments = parser.parse_args()
    print(read_service_tier(arguments.thread_id, arguments.turn_id) or "")
