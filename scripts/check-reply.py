#!/usr/bin/env python3
"""Check mechanically verifiable reply formatting, never semantic correctness."""
import argparse
from pathlib import Path
import re

MARKERS = {'⮑', '✅', '❌', '👀', '🐌', '🐞', 'ⓘ', '🫵', '🤨', '⚠️', '❓', '💡', '⚖️', '⛔', '🎯', '➕➕', '🖥️', '👉'}
MARKER = re.compile(r'\\\(\\(huge|Huge)\\text\{([^{}]+)\}\\\)')
# Nested underlines do not exempt a highlight from palette/font/link checks.
COLOUR = re.compile(r'\\\(\\color\{([^{}]+)\}\{\\(textsf|textrm)\{.*?\}\}\\\)')
LINK = re.compile(r'\[([^\]\n]*)\]\((<[^>\n]+>|[^)\n]+)\)')
PALETTE = {'#ef4444', '#22c55e', '#fb923c', '#67e8f9'}
CARET = r'\(\LARGE\text{⌄}\)'


def check(text, check_paths=True, approved_project_markers=(), require_pointer=True):
    errors = []
    previous = ''
    has_pointer = False
    fence = None
    for number, raw in enumerate(text.splitlines(), 1):
        stripped = raw.lstrip()
        opening = re.match(r'(`{3,}|~{3,})', stripped)
        if opening:
            token = opening.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        # Quoted user/earlier-assistant context is evidence, not a new reply.
        if stripped.startswith('>'):
            previous = raw
            continue
        line = re.sub(r'(`+).*?\1', '', raw)
        def fail(message):
            errors.append(f'Line {number}: {message}')
        if '<!--' in line:
            fail('Keep hidden comments and notification metadata out of the reply.')
        for match in MARKER.finditer(line):
            if match.group(2) in {'🫵', '👉'}:
                has_pointer = True
            if match.group(2) == '👉' and line[match.end():].strip() in {'', CARET}:
                fail('Put the reading pointer inline immediately before its takeaway.')
            if match.group(1) != 'huge':
                fail('Use lowercase \\huge for section markers.')
            if match.group(2) not in MARKERS | set(approved_project_markers):
                fail('Use an approved marker without substitutions or combinations.')
            if match.group(2) != '👉' and (line[:match.start()].strip() or raw.startswith((' ', '\t'))):
                fail('Place the marker first and left-aligned, before its text.')
            tail = line[match.end():].strip()
            if not tail:
                fail('Add the approved enlarged ⌄ after a standalone section marker.')
            elif tail in {'▾', '∨', '⌄'}:
                fail('Replace the old tiny caret with the approved enlarged ⌄.')
            elif (tail.startswith(('▾', '∨', '⌄')) or tail.startswith(CARET)) and tail != CARET:
                fail('The chevron belongs only beside a standalone section marker, not inline text.')
            if match.group(2) == '⮑' and tail in {'', '▾', '∨', CARET}:
                fail('Keep the return arrow beside the opening answer, even when a table or list follows.')
            if match.group(2) == '⮑' and not previous.lstrip().startswith('>'):
                fail('Put the relevant question/excerpt in a blockquote just above the answer.')
        if re.match(r'[\U0001F300-\U0001FAFF⮑ⓘ✅❌⚠⛔➕]', stripped) and not stripped.startswith('|'):
            fail('Render a section marker with the approved lowercase \\huge wrapper.')
        for match in COLOUR.finditer(line):
            colour, font = match.group(1, 2)
            if colour == 'magenta':
                if font != 'textrm':
                    fail('Skill names use upright serif \\textrm in magenta.')
                if not re.match(r'\s*\[↗\]\(', line[match.end():]):
                    fail('Follow each magenta skill name with its own clickable ↗.')
            elif colour not in PALETTE or font != 'textsf':
                fail('Use an approved highlight colour with normal-size \\textsf.')
        if re.search(r'(?:\*\*)?Skill use:', line):
            current_marker = MARKER.match(line)
            prior_marker = MARKER.fullmatch(previous.strip().removesuffix(' ' + CARET))
            if not any(m and m.group(2) == '🎯' for m in [current_marker, prior_marker]):
                fail('Start skill announcements with 🎯.')
            if not any(m.group(1) == 'magenta' and m.group(2) == 'textrm' for m in COLOUR.finditer(line)):
                fail('Skill announcements need magenta upright-serif skill names and adjacent ↗ links.')
        for match in LINK.finditer(line):
            label, target = match.groups()
            target = target.strip('<>')
            if '\\color' in label:
                fail('Keep coloured LaTeX outside the link label; link an adjacent ↗.')
            if label.lower() in {'open', 'open skill'}:
                fail('Use ↗, not an opening-word label.')
            path = re.sub(r':\d+$', '', target)
            if path.startswith('/'):
                if path.lower().endswith('.md'):
                    fail('Generate an HTML viewer for a Markdown reference.')
                if check_paths and not Path(path).exists():
                    fail('The local link destination does not exist: ' + path)
        if line.strip():
            previous = line
    if require_pointer and not has_pointer:
        errors.append('Include 🫵 for a real user action, or 👉 before the main reading takeaway.')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reply', type=Path)
    parser.add_argument('--skip-path-check', action='store_true', help='For portable fixtures only; real replies must verify destinations.')
    parser.add_argument('--approved-project-marker', action='append', default=[], help='Exact symbol already approved by the user for this project; repeat for each mapping.')
    args = parser.parse_args()
    errors = check(args.reply.read_text(encoding='utf-8'), not args.skip_path_check, args.approved_project_marker)
    print('\n'.join(errors) if errors else 'Reply structure passed. Meaning, coverage and visual appearance still need review.')
    raise SystemExit(bool(errors))
