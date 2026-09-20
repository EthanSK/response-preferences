#!/usr/bin/env python3
"""Check mechanically verifiable reply formatting, never semantic correctness."""
import argparse
from pathlib import Path
import re
import importlib.util

_spec = importlib.util.spec_from_file_location('reply_math', Path(__file__).with_name('math-validation.py'))
math_validation = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(math_validation)

MARKERS = {'🧪', '🛠️', '⮑', '✅', '❌', '👀', '🐌', '🐞', 'ⓘ', '🫵', '🤨', '⚠️', '❓', '💡', '⚖️', '⛔', '🧠', '➕➕', '🖥️', '👉'}
MARKER = re.compile(r'\\\((?:\\([a-zA-Z]+))?\\text\{([^{}]+)\}\\\)')
# Match plain leading markers too, so commentary still checks vocabulary and placement.
# The empty first group keeps the same (size, symbol) shape as wrapped markers.
PLAIN_MARKER = re.compile(r'()(➕➕|[\U0001F300-\U0001FAFF⮑ⓘ✅❌⚠⛔➕⚖❓][\ufe0f]?)')
# Nested underlines do not exempt a highlight from palette/font/link checks.
COLOUR = re.compile(r'\\\(\\color\{([^{}]+)\}\{\\(textsf|textrm)\{.*?\}\}\\\)')
COLOUR_COMMAND = re.compile(r'\\color\{([^{}]+)\}')
LINK = re.compile(r'\[([^\]\n]*)\]\((<[^>\n]+>|[^)\n]+)\)')
ANNOTATION = re.compile(r':codex-annotation\{index="([0-9]+)"\}')
ANNOTATION_CONTEXT_LABELS = ('Problem at hand', 'Earlier response', 'Your annotation')
INLINE_CODE = re.compile(r'(?<!`)`[^`\n]+`(?!`)')
PALETTE = {'#ef4444', '#22c55e', '#fb923c', '#67e8f9'}
TOPIC_COLOUR = '#b8a4d9'
CARET = r'\(\raisebox{0.3em}{\Large\text{⌄}}\)'
WORKING_CARET = '⌄'
# Each expression is selectable but unbreakable. Short chunks give the browser
# real spaces between expressions where it can wrap.
MAX_PROSE_CHARACTERS = 64
INLINE_MATH = re.compile(r'\\\((.*?)\\\)')
# An even run of backslashes does not escape TeX's comment character.
UNESCAPED_PERCENT = re.compile(r'(?<!\\)(?:\\\\)*%')


def has_text_underscore(expression):
    """Catch literal underscores in text wrappers, preserving math subscripts."""
    modes = [False]
    pending = None
    for token in re.findall(r'\\[A-Za-z]+|\\.|[^\\]', expression):
        if token.startswith('\\'):
            if token in {r'\textsf', r'\textrm', r'\text'}:
                pending = True
            elif token == r'\ensuremath':
                pending = False
            continue
        if token == '{':
            modes.append(modes[-1] if pending is None else pending)
            pending = None
        elif token == '}' and len(modes) > 1:
            modes.pop()
        elif token == '$':
            modes[-1] = not modes[-1]
        elif token == '_' and modes[-1]:
            return True
        elif not token.isspace():
            pending = None
    return False


def prose_length(expression):
    """Approximate visible text in the supported inline prose syntax, not TeX math."""
    if not re.search(r'\\(?:textsf|textrm|text)\{', expression):
        return 0
    # Remove command arguments that are not visible text before stripping wrappers.
    visible = re.sub(r'\\(?:color|textcolor|raisebox)\{[^{}]*\}', '', expression)
    visible = re.sub(r'\\[A-Za-z]+\s*', '', visible)
    visible = re.sub(r'\\([^A-Za-z])', r'\1', visible)
    return len(re.sub(r'\s+', ' ', visible.replace('{', '').replace('}', '')).strip())


def group_end(expression, opening):
    """Return the matching closing brace, respecting TeX commands and escapes."""
    depth = 1
    index = opening + 1
    while index < len(expression):
        if expression[index] == '\\':
            command = re.match(r'\\[A-Za-z]+', expression[index:])
            index += len(command.group(0)) if command else 2
            continue
        if expression[index] == '{':
            depth += 1
        elif expression[index] == '}':
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return len(expression)


def has_unwrapped_underline(expression):
    """Reject prose underlines that KaTeX would render as space-free maths."""

    text_ranges = []
    for match in re.finditer(r'\\(?:textsf|textrm|text)\{', expression):
        opening = match.end() - 1
        text_ranges.append((opening, group_end(expression, opening)))
    for match in re.finditer(r'\\underline\{', expression):
        argument = match.end()
        if re.match(r'\\(?:textsf|textrm|text)\{', expression[argument:]):
            continue
        if any(start < match.start() < end for start, end in text_ranges):
            continue
        return True
    return False


def formatted_text_word_counts(expression):
    """Return word counts for outer text wrappers: each is one browser box."""
    counts = []
    consumed_until = -1
    for match in re.finditer(r'\\(?:textsf|textrm|text)\{', expression):
        if match.start() < consumed_until:
            continue
        opening = match.end() - 1
        closing = group_end(expression, opening)
        consumed_until = closing
        argument = expression[opening + 1:closing]
        visible = re.sub(r'\\[A-Za-z]+\s*', '', argument)
        visible = re.sub(r'\\([^A-Za-z])', r'\1', visible)
        visible = visible.replace('{', '').replace('}', '')
        counts.append(len(re.findall(r'\S+', visible)))
    return counts


def leading_marker(line):
    return MARKER.match(line) or PLAIN_MARKER.match(line)


def check(text, check_paths=True, approved_project_markers=(), require_pointer=True, commentary=False, hover_contexts=(), require_topic=True):
    errors = math_validation.check_math(text)
    topic_lines = []
    annotation_context_counts = dict.fromkeys(ANNOTATION_CONTEXT_LABELS, 0)
    seen_annotation_indexes = set()
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
            context_line = stripped[1:].strip().replace('**', '')
            for label in ANNOTATION_CONTEXT_LABELS:
                if context_line.startswith(label + ':') and context_line[len(label) + 1:].strip():
                    annotation_context_counts[label] += 1
            previous = raw
            continue
        line = re.sub(r'(`+).*?\1', '', raw)
        def fail(message):
            errors.append(f'Line {number}: {message}')
        if not commentary:
            for annotation in ANNOTATION.finditer(line):
                index = annotation.group(1)
                if index in seen_annotation_indexes:
                    continue
                seen_annotation_indexes.add(index)
                for label in ANNOTATION_CONTEXT_LABELS:
                    if annotation_context_counts[label] < len(seen_annotation_indexes):
                        fail(f'Annotation {index} needs its own quoted {label}: context before the answer/reference. The short rainbow question and native popup do not replace it.')
        for expression in INLINE_MATH.finditer(line):
            if UNESCAPED_PERCENT.search(expression.group(1)):
                fail(r'Escape literal percent signs inside LaTeX as \%; bare % starts a TeX comment and can break rendering. Leave ordinary Markdown percentages unchanged.')
            if has_text_underscore(expression.group(1)):
                fail(r'Escape literal underscores in LaTeX text as \_, or keep identifiers in ordinary inline code and underline surrounding prose. Bare _ in text can expose red raw syntax.')
            if has_unwrapped_underline(expression.group(1)):
                fail(r'Wrap underlined prose in \textsf: use \underline{\textsf{Words}} or place \underline{Words} inside an existing \textsf group. A bare \underline{Words} renders as maths, removing spaces and italicising letters.')
            if prose_length(expression.group(1)) > MAX_PROSE_CHARACTERS:
                fail('A selectable LaTeX chunk exceeds 64 approximate visible characters and may overflow. Split the paragraph into consecutive short \\textsf expressions with ordinary spaces between them.')
        prose_expressions = [m for m in INLINE_MATH.finditer(line)
                             if prose_length(m.group(1)) > 1 and not MARKER.fullmatch(m.group(0))]
        if prose_expressions and 'Skill use:' not in line:
            remainder = line
            for match in reversed(list(INLINE_MATH.finditer(line))):
                remainder = remainder[:match.start()] + remainder[match.end():]
            remainder = ANNOTATION.sub('', remainder)
            remainder = LINK.sub('', remainder)
            remainder = INLINE_CODE.sub('', remainder)
            remainder = re.sub(r'^[\s>*#\-+\d.)]+', '', remainder)
            if re.search(r'[A-Za-z0-9]', remainder):
                fail('Put paragraph prose inside consecutive short LaTeX text chunks; keep only markers, links, code or punctuation outside.')
        if '<!--' in line:
            fail('Keep hidden comments and notification metadata out of the reply.')
        if re.search(r'</?u(?:\s[^>]*)?>', line, re.IGNORECASE):
            fail(r'Never use HTML <u> tags in a reply; Codex can display them literally. Use \(\underline{\textsf{Words}}\) instead.')
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
                # The closing reminder is one selectable lavender expression.
                parts = list(COLOUR.finditer(line))
                prefix = r'\(\color{#b8a4d9}{\textsf{About: '
                valid = (line.strip().startswith(prefix)
                         and line.count(r'\textsf{About: ') == 1
                         and not COLOUR.sub('', line).strip()
                         and all(p.group(1) == TOPIC_COLOUR and p.group(2) == 'textsf' for p in parts)
                         and all(p.group(0).split(r'\textsf{', 1)[1].removesuffix(r'}}\)').removeprefix('About: ').strip() for p in parts))
                if not valid:
                    fail('Use muted lavender only for one closing About: reminder, split into short normal-size \\textsf chunks when needed.')
                if number not in topic_lines:
                    topic_lines.append(number)
                if number != last_line:
                    fail('Put the topic reminder at the very end, after all other message content.')
            elif colour not in PALETTE or font != 'textsf':
                fail('Use an approved highlight colour with normal-size \\textsf.')
        for expression in INLINE_MATH.finditer(line):
            for colour in COLOUR_COMMAND.findall(expression.group(1)):
                if colour not in PALETTE | {TOPIC_COLOUR, 'magenta'}:
                    fail('Use an approved highlight colour inside the short paragraph chunk.')
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
    if commentary and topic_lines:
        errors.append('Reserve the About: topic reminder for the final reply, not working commentary.')
    elif not commentary and require_topic and len(topic_lines) != 1:
        errors.append('End the final reply with exactly one muted-lavender About: topic reminder.')
    if require_pointer and not has_pointer:
        errors.append('Include 🫵 for a real user action, or 👉 before the main reading takeaway.')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reply', type=Path)
    parser.add_argument('--commentary', action='store_true', help='Check a work update: plain normal-size markers; attention fingers and About reminders are forbidden.')
    parser.add_argument('--skip-path-check', action='store_true', help='For portable fixtures only; real replies must verify destinations.')
    parser.add_argument('--approved-project-marker', action='append', default=[], help='Exact symbol already approved by the user for this project; repeat for each mapping.')
    parser.add_argument('--hover-context', action='append', default=[], help='Exact user-approved hover-only destination; real file links remain checked.')
    args = parser.parse_args()
    errors = check(args.reply.read_text(encoding='utf-8'), not args.skip_path_check, args.approved_project_marker, require_pointer=not args.commentary, commentary=args.commentary, hover_contexts=args.hover_context)
    print('\n'.join(errors) if errors else 'Reply structure passed. Meaning, coverage and visual appearance still need review.')
    raise SystemExit(bool(errors))
