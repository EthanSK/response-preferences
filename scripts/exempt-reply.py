#!/usr/bin/env python3
"""Prepare a task/reply-specific exception for an explicit user format request."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid

spec = importlib.util.spec_from_file_location('reply_guard', Path(__file__).with_name('guard-reply.py'))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def prepare(payload, home):
    request = payload.get('request')
    if payload.get('reason') != 'explicit_user_format' or not isinstance(request, str) or not request.strip():
        raise ValueError('Quote the explicit user format instruction in request; reason must be explicit_user_format')
    reply = Path(payload['reply_file']).read_text(encoding='utf-8')
    if not reply.strip():
        raise ValueError('An exact final reply is required')
    destination = guard.exemption_path(home, payload['session_id'], reply)
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = destination.with_suffix('.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('x', encoding='utf-8') as output:
            os.chmod(temporary, 0o600)
            json.dump({'reason': payload['reason'], 'request': request}, output)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: exempt-reply.py payload.json')
    payload = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    home = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex'))
    print(json.dumps({'prepared': True, 'path': str(prepare(payload, home))}))
