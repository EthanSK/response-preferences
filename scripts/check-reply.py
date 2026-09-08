#!/usr/bin/env python3
"""Check mechanically verifiable reply formatting, never semantic correctness."""
import argparse
from pathlib import Path
import re

MARKERS = {'🧪', '🛠️', '⮑', '✅', '❌', '👀', '🐌', '🐞', 'ⓘ', '🫵', '🤨', '⚠️', '❓', '💡', '⚖️', '⛔', '🧠', '➕➕', '🖥️', '👉'}
MARKER = re.compile(r'\\\((?:\\([a-zA-Z]+))?\\text\{([^{}]+)\}\\\)')
# Match plain leading markers too, so commentary still checks vocabulary and placement.
# The empty first group keeps the same (size, symbol) shape as wrapped markers.
PLAIN_MARKER = re.compile(r'()(➕➕|[\U0001F300-\U0001FAFF⮑ⓘ✅❌⚠⛔➕⚖❓][\ufe0f]?)')
# Nested underlines do not exempt a highlight from palette/font/link checks.
COLOUR = re.compile(r'\\\(\\color\{([^{}]+)\}\{\\(textsf|textrm)\{.*?\}\}\\\)')
LINK = re.compile(r'\[([^\]\n]*)\]\((<[^>\n]+>|[^)\n]+)\)')
PALETTE = {'#ef4444', '#22c55e', '#fb923c', '#67e8f9'}
TOPIC_COLOUR = '#b8a4d9'
CARET = r'\(\raisebox{0.3em}{\Large\text{⌄}}\)'
WORKING_CARET = '⌄'
# Authoring guardrail only: glyph widths and the available pane still vary.
MAX_PROSE_CHARACTERS = 80
INLINE_MATH = re.compile(r'\\\((.*?)\\\)')
# An even run of backslashes does not escape TeX's comment character.
UNESCAPED_PERCENT = re.compile(r'(?<!\\)(?:\\\\)*%')


def prose_length(expression):
    """Approximate visible text in the supported inline prose syntax, not TeX math."""
    if not re.search(r'\\(?:textsf|textrm|text)\{', expression):
        return 0
    # Remove command arguments that are not visible text before stripping wrappers.
    visible = re.sub(r'\\(?:color|textcolor|raisebox)\{[^{}]*\}', '', expression)
    visible = re.sub(r'\\[A-Za-z]+\s*', '', visible)
    visible = re.sub(r'\\([^A-Za-z])', r'\1', visible)
    return len(re.sub(r'\s+', ' ', visible.replace('{', '').replace('}', '')).strip())


def leading_marker(line):
    return MARKER.match(line) or PLAIN_MARKER.match(line)


def check(text, check_paths=True, approved_project_markers=(), require_pointer=True, commentary=False, hover_contexts=(), require_topic=True):
    errors = []
    topic_lines = []
    last_line = max((i for i, line in enumerate(text.splitlines(), 1) if line.strip()), default=0)
    previous = ''
    has_pointer = False
    fence = None
    caret = WORKING_CARET if commentary else CARET
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
        for expression in INLINE_MATH.finditer(line):
            if UNESCAPED_PERCENT.search(expression.group(1)):
                fail(r'Escape literal percent signs inside LaTeX as \%; bare % starts a TeX comment and can break rendering. Leave ordinary Markdown percentages unchanged.')
            if prose_length(expression.group(1)) > MAX_PROSE_CHARACTERS:
                fail('Inline LaTeX prose exceeds 80 approximate visible characters and may overflow. Use a shorter self-contained highlight and ordinary wrapping details; keep underline cues short too.')
        if '<!--' in line:
            fail('Keep hidden comments and notification metadata out of the reply.')
        matches = list(MARKER.finditer(line))
        plain = PLAIN_MARKER.match(line, len(line) - len(line.lstrip()))
        if plain:
            matches.insert(0, plain)
        for match in matches:
            if match.group(2) in {'🫵', '👉'}:
                has_pointer = True
                if commentary:
                    fail('Reserve attention fingers for the final reply, not working commentary.')
            if match.group(2) == '👉' and line[match.end():].strip() in {'', CARET, WORKING_CARET}:
                fail('Put the reading pointer inline immediately before its takeaway.')
            if commentary and match.re is MARKER:
                fail('Use plain normal-size markers in working commentary, without LaTeX size wrappers.')
            elif not commentary and match.group(1) != 'huge':
                fail('Use lowercase \\huge for section markers.')
            if match.group(2) not in MARKERS | set(approved_project_markers):
                fail('Use an approved marker without substitutions or combinations.')
            if match.group(2) != '👉' and (line[:match.start()].strip() or raw.startswith((' ', '\t'))):
                fail('Place the marker first and left-aligned, before its text.')
            tail = line[match.end():].strip()
            if not tail:
                fail('Add the approved ⌄ after a standalone section marker, using this reply phase’s size.')
            elif tail in {'▾', '∨', WORKING_CARET, CARET, r'\(\LARGE\text{⌄}\)', r'\(\Large\text{⌄}\)'} and tail != caret:
                fail('Use the approved ⌄ size for this reply phase.')
            elif (tail.startswith(('▾', '∨', '⌄')) or tail.startswith(CARET)) and tail != caret:
                fail('The chevron belongs only beside a standalone section marker, not inline text.')
            if match.group(2) == '⮑' and tail in {'', '▾', '∨', CARET, WORKING_CARET}:
                fail('Keep the return arrow beside the opening answer, even when a table or list follows.')
            if match.group(2) == '⮑' and not previous.lstrip().startswith('>'):
                fail('Put the relevant question/excerpt in a blockquote just above the answer.')
        for match in COLOUR.finditer(line):
            colour, font = match.group(1, 2)
            if colour == 'magenta':
                if font != 'textrm':
                    fail('Skill names use upright serif \\textrm in magenta.')
                if not re.match(r'\s*\[↗\]\(', line[match.end():]):
                    fail('Follow each magenta skill name with its own clickable ↗.')
            elif colour == TOPIC_COLOUR:
                # A single closing reminder may use several short boxes to wrap.
                parts = list(COLOUR.finditer(line))
                prefix = r'\(\color{#b8a4d9}{\textsf{About: '
                valid = (line.strip().startswith(prefix)
                         and line.count(r'\textsf{About: ') == 1
                         and not COLOUR.sub('', line).strip()
                         and all(p.group(1) == TOPIC_COLOUR and p.group(2) == 'textsf' for p in parts)
                         and all(p.group(0).split(r'\textsf{', 1)[1].removesuffix(r'}}\)').removeprefix('About: ').strip() for p in parts))
                if not valid:
                    fail('Use muted lavender only for one closing About: reminder in normal-size \\textsf, optionally split into short colour expressions.')
                if number not in topic_lines:
                    topic_lines.append(number)
                if number != last_line:
                    fail('Put the topic reminder at the very end, after all other message content.')
            elif colour not in PALETTE or font != 'textsf':
                fail('Use an approved highlight colour with normal-size \\textsf.')
        if re.search(r'(?:\*\*)?Skill use:', line):
            current_marker = leading_marker(line)
            prior = previous.strip().removesuffix(' ' + caret)
            prior_marker = leading_marker(prior)
            if prior_marker and prior_marker.end() != len(prior):
                prior_marker = None
            if not any(m and m.group(2) == '🧠' for m in [current_marker, prior_marker]):
                fail('Start skill announcements with 🧠.')
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
                if check_paths and not (label == '↗' and target in hover_contexts) and not Path(path).exists():
                    fail('The local link destination does not exist: ' + path)
        if line.strip():
            previous = line
    if require_topic and len(topic_lines) != 1:
        errors.append('End every message with exactly one muted-lavender About: topic reminder.')
    if require_pointer and not has_pointer:
        errors.append('Include 🫵 for a real user action, or 👉 before the main reading takeaway.')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reply', type=Path)
    parser.add_argument('--commentary', action='store_true', help='Check a work update: plain normal-size markers; attention fingers are forbidden.')
    parser.add_argument('--skip-path-check', action='store_true', help='For portable fixtures only; real replies must verify destinations.')
    parser.add_argument('--approved-project-marker', action='append', default=[], help='Exact symbol already approved by the user for this project; repeat for each mapping.')
    parser.add_argument('--hover-context', action='append', default=[], help='Exact user-approved hover-only destination; real file links remain checked.')
    args = parser.parse_args()
    errors = check(args.reply.read_text(encoding='utf-8'), not args.skip_path_check, args.approved_project_marker, require_pointer=not args.commentary, commentary=args.commentary, hover_contexts=args.hover_context)
    print('\n'.join(errors) if errors else 'Reply structure passed. Meaning, coverage and visual appearance still need review.')
    raise SystemExit(bool(errors))
