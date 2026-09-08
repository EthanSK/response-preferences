"""Validate authored math with the bundled KaTeX renderer, not a character whitelist."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess


def expressions(text):
    """Extract explicit math delimiters outside Markdown code and quoted evidence."""
    masked = []
    fence = None
    for raw in text.splitlines(keepends=True):
        stripped = raw.lstrip()
        token = re.match(r'(`{3,}|~{3,})', stripped)
        skip = fence is not None or stripped.startswith('>')
        if token:
            skip = True
            mark = token.group(1)
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence):
                fence = None
        if skip:
            masked.append(re.sub(r'[^\n]', ' ', raw))
        else:
            masked.append(re.sub(r'(`+).*?\1', lambda m: ' ' * len(m[0]), raw))
    source = ''.join(masked)
    spans, errors = [], []
    active = None
    pairs = {r'\(': r'\)', r'\[': r'\]', '$$': '$$'}
    for match in re.finditer(r'\\[()[\]]|\$\$', source):
        start = match.start()
        preceding = len(source[:start]) - len(source[:start].rstrip('\\'))
        if preceding % 2:
            continue
        token = match[0]
        line = source.count('\n', 0, start) + 1
        if active and token == pairs[active[0]]:
            spans.append((active[2], source[active[1]:start]))
            active = None
        elif active:
            errors.append(f'Line {line}: Mismatched or nested LaTeX delimiter.')
        elif token in pairs:
            active = (token, match.end(), line)
        else:
            errors.append(f'Line {line}: LaTeX closing delimiter has no opening delimiter.')
    if active:
        errors.append(f'Line {active[2]}: LaTeX opening delimiter has no closing delimiter.')
    return spans, errors


def render_errors(values):
    """One bounded subprocess per draft; unavailable validation cannot pass."""
    if not values:
        return []
    # Desktop hooks may inherit a smaller PATH than an interactive shell.
    common_bins = [Path.home() / 'bin', Path.home() / '.local/bin', Path('/opt/homebrew/bin'), Path('/usr/local/bin'), Path('/usr/bin')]
    node = (os.environ.get('RESPONSE_PREFERENCES_NODE') or shutil.which('node')
            or shutil.which('node', path=os.pathsep.join(map(str, common_bins))))
    if not node:
        return ['Renderer validation unavailable: put Node.js on PATH or set RESPONSE_PREFERENCES_NODE.'] * len(values)
    try:
        result = subprocess.run(
            [node, str(Path(__file__).with_name('render-math.cjs'))],
            input=json.dumps(values), text=True, capture_output=True, timeout=8,
        )
        parsed = json.loads(result.stdout) if result.returncode == 0 else None
        if not isinstance(parsed, list) or len(parsed) != len(values) or any(x is not None and not isinstance(x, str) for x in parsed):
            raise ValueError('Invalid renderer result')
        return parsed
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return ['Renderer validation unavailable or failed; do not claim this draft passed.'] * len(values)


def check_math(text):
    spans, errors = expressions(text)
    for (line, _), error in zip(spans, render_errors([value for _, value in spans])):
        if error:
            errors.append(f'Line {line}: {error}. Keep literal names/numbers in Markdown or inline code, or correct the TeX and recheck.')
    return errors
