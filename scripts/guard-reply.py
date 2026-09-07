#!/usr/bin/env python3
"""Conservative final-reply checks for an optional completion-hook adapter.

No transcript reads, network, message edits, notifications or persistent state.
The caller owns routing, user opt-outs and the one-continuation limit.
"""
import importlib.util
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid

spec = importlib.util.spec_from_file_location('response_reply_check', Path(__file__).with_name('check-reply.py'))
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def visible_reply(text):
    return re.sub(r'\s*<oai-mem-citation>.*?</oai-mem-citation>\s*$', '', text.replace('\r\n', '\n'), flags=re.S).strip()


def exemption_path(home, session_id, text):
    digest = hashlib.sha256(visible_reply(text).encode('utf-8')).hexdigest()
    return Path(home) / 'hooks/response-style-exemptions' / str(uuid.UUID(session_id)) / (digest + '.json')


def is_exempt(home, session_id, text):
    """Read an authored exact-format exception bound to this task and reply."""
    try:
        data = json.loads(exemption_path(home, session_id, text).read_text())
        return (data.get('reason') == 'explicit_user_format'
                and isinstance(data.get('request'), str) and bool(data['request'].strip()))
    except (OSError, ValueError, TypeError, AttributeError):
        return False


def prose_lines(text):
    lines = []
    fence = None
    for line in text.splitlines():
        s = line.strip()
        token = re.match(r'(`{3,}|~{3,})', s)
        if token:
            if fence is None:
                fence = token[1]
            elif token[1][0] == fence[0] and len(token[1]) >= len(fence):
                fence = None
            continue
        if fence or s.startswith(('>', '|', '#')) or not s or '#b8a4d9' in s:
            continue
        lines.append(line)
    return '\n'.join(lines)


def errors_for(text):
    if not isinstance(text, str):
        return []
    text = visible_reply(text)
    if not text:
        return []
    # Do not break machine-readable/exact artifact responses with decorative prose.
    try:
        json.loads(text)
        return []
    except (ValueError, TypeError):
        pass
    prose = prose_lines(text)
    if not prose:
        return []
    # The hook lacks project instructions and exact original-message hover values.
    # Leave vocabulary approval and local destinations to the explicit draft check.
    extensions = {m[2] for m in checker.MARKER.finditer(text)}
    extensions.update(m[2] for line in text.splitlines() if (m := checker.PLAIN_MARKER.match(line)))
    errors = checker.check(text, check_paths=False, approved_project_markers=extensions)
    if len(re.findall(r'\b[^\W\d_]{2,}\b', prose)) >= 5 and r'\underline{' not in prose:
        errors.append('The prose has no underlined scanning cues. Add short subject-bearing cues, preserving negatives and qualifications.')
    return list(dict.fromkeys(errors))[:8]


def repair_context(errors, skill_dir):
    return ('The final reply has response-style omissions: ' + '; '.join(errors) + '. '
            'Read the compact response-preferences core at ' + str(Path(skill_dir) / 'SKILL.md') + '. '
            'Make one formatting-only correction of the answer to the ORIGINAL user request. '
            'Preserve facts, qualifications, completed work, code, quotations and real annotation directives. '
            'Do not rerun domain work, invent new progress, or answer this hook message as the user question. '
            'Honour any explicit user instruction requiring an exact format over these style defaults. '
            'For that case only, preserve the exact answer and use scripts/exempt-reply.py as documented in references/reliability.md; do not add decoration. '
            'Run check-reply.py on the corrected draft and prepare its matching notification summary if installed. '
            'This check cannot judge semantic emphasis or hide already streamed text.')


if __name__ == '__main__':
    payload = json.load(sys.stdin)
    errors = errors_for(payload.get('last_assistant_message'))
    output = {'errors': errors}
    if errors:
        output['additionalContext'] = repair_context(errors, Path(__file__).resolve().parents[1])
        if not payload.get('stop_hook_active'):
            output.update(decision='block', reason=output['additionalContext'])
        else:
            output['systemMessage'] = 'Response-style omissions remain after the bounded correction; no further automatic retry.'
    print(json.dumps(output))
