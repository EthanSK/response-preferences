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
    spans, errors, protected = [], [], []
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
            protected.append((active[3], match.end()))
            active = None
        elif active:
            errors.append(f'Line {line}: Mismatched or nested LaTeX delimiter.')
        elif token in pairs:
            active = (token, match.end(), line, match.start())
        else:
            errors.append(f'Line {line}: LaTeX closing delimiter has no opening delimiter.')
    if active:
        errors.append(f'Line {active[2]}: LaTeX opening delimiter has no closing delimiter.')
        protected.append((active[3], len(source)))

    # A response-formatting command outside explicit math delimiters renders as
    # raw red TeX in Codex. Keep quoted evidence/code excluded by the mask above,
    # and reject the authored leak before a user ever sees it.
    outside = list(source)
    for start, end in protected:
        outside[start:end] = ' ' * (end - start)
    outside = ''.join(outside)
    commands = re.compile(r'\\(?:underline|textsf|textrm|text|textcolor|color|huge|Huge|large|Large|LARGE|raisebox)\s*\{')
    reported_lines = set()
    for match in commands.finditer(outside):
        line = outside.count('\n', 0, match.start()) + 1
        if line in reported_lines:
            continue
        reported_lines.add(line)
        errors.append(
            f'Line {line}: LaTeX formatting command is outside explicit math delimiters. '
            r'Wrap the whole expression in \( and \), and do not add a stray backslash before the closing delimiter.'
        )
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


# Claude desktop's Markdown parser passes \(...\) to KaTeX only when an inline
# guard accepts it; otherwise the source shows as plain text such as
# "(\textsf{...})". These rules mirror that guard as read from claude.ai asset
# ce044ea01-CdYn2J6_.js on 2026-10-21. Its remaining conditions always hold for
# the \textsf, \underline and \color expressions this skill writes. Re-read the
# guard if Claude starts showing other expressions raw.
CLAUDE_MAX_BODY_CHARACTERS = 200
CLAUDE_REJECTED_BODY = re.compile(r'[$`]|\\[(|.+*?0-9]')
CLAUDE_REJECTED_FIXES = {
    '$': r'a dollar sign, even escaped as \$. Write \textdollar{}500 inside the expression, or keep $500 in ordinary Markdown',
    '`': 'a backtick. Keep code in ordinary inline code outside the expression',
}


def claude_raw_errors(text):
    """List expressions Claude desktop would show as raw text, including blockquoted reminders."""
    errors = []
    fence = None
    for number, raw in enumerate(text.splitlines(), 1):
        token = re.match(r'(`{3,}|~{3,})', raw.lstrip())
        if token:
            mark = token.group(1)
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        # Claude strips blockquote markers before the guard sees the line.
        line = re.sub(r'(`+).*?\1', lambda m: ' ' * len(m[0]), re.sub(r'^\s*(?:>\s?)+', '', raw))
        for match in re.finditer(r'\\\((.*?)\\\)', line):
            body = match.group(1)
            # Emphasis markers may sit between the expression and its required boundary.
            before = line[:match.start()].rstrip('*_~')
            if before and before[-1] not in ' \t([':
                errors.append(f'Line {number}: Claude shows this expression as raw text because "{before[-1]}" touches its opening \\(. Put a space, ( or [ before \\(.')
            if len(body) > CLAUDE_MAX_BODY_CHARACTERS:
                errors.append(f'Line {number}: Claude shows this {len(body)}-character expression as raw text; its limit is {CLAUDE_MAX_BODY_CHARACTERS} characters between \\( and \\). Shorten it or split it into separate expressions.')
            rejected = CLAUDE_REJECTED_BODY.search(body)
            if rejected:
                found = rejected.group(0)
                fix = CLAUDE_REJECTED_FIXES.get(found, f'{found}. Remove that backslash or keep the text in ordinary Markdown')
                errors.append(f'Line {number}: Claude shows this expression as raw text because it contains {fix}.')
    return errors
