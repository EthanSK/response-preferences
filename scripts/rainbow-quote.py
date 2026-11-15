#!/usr/bin/env python3
"""Generate vivid question references without storing gradient tables.

Run ``python3 scripts/rainbow-quote.py question.txt``; one shared word counter
keeps colour destinations changing across replies. Explicit positions reproduce
examples without touching that counter.
"""
from __future__ import annotations

import argparse
import html
import importlib.util
from pathlib import Path
import math
import re
import os
import fcntl
import tempfile
from collections.abc import Iterable

MAX_CHARS = 24
MAX_GROUP_CHARS = 64
MAX_QUOTE_CHARS = 80
ESCAPES = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '#': r'\#',
           '%': r'\%', '_': r'\_', '&': r'\&', '$': r'\$',
           '^': r'\textasciicircum{}', '~': r'\textasciitilde{}'}
# Claude desktop shows any expression containing $ as raw text, even escaped,
# and any expression over 200 source characters. Eight coloured words stay
# under that limit; math-validation.py checks the exact rules.
CLAUDE_ESCAPES = {**ESCAPES, '$': r'\textdollar{}'}
CLAUDE_MAX_WORDS = 8

# Colour route. Ethan calls this "rainbow text"; his "index" is the shared word
# position below, and "different next colors it transitions to" are the blend
# destinations. Every BLEND_WORDS words the colour reaches a new destination,
# then blends evenly to the next. Destinations come from a formula, not a list:
#
#   destination(b) = (TURN*b + HALF_TURN*flip(b) + nudge(b)) mod TICKS
#
# flip and nudge are scrambled from the blend number b. Consecutive
# destinations therefore differ by TURN plus a nudge difference (forwards,
# about 77-138 degrees) when the flips match, or by TURN - HALF_TURN plus a
# nudge difference (about 42-104 degrees backwards) when they differ. Directions
# are approximately balanced in samples, averaging about 15 degrees per word.
# Every native vivid shade can be a destination: the initial 144-tick prototype
# repeated 259 of 10,000 sampled 12-word profiles; this resolution repeated none.
# This is a fixed amount of integer arithmetic per word, with no replay of old
# words. Arithmetic on exceptionally large integers still scales with bit size.
BRIGHT, DIM = 250, 112
TICKS = 6 * (BRIGHT - DIM)   # 828 destinations: every distinct shade on the ring
BLEND_WORDS = 6              # words per blend; steady for every blend
UNITS = TICKS * BLEND_WORDS  # exact substeps between destination shades
SECTOR = UNITS // 6          # red, yellow, green, cyan, blue and magenta corners
TURN = 247                   # about 107.4 degrees; coprime with 828
HALF_TURN = TICKS // 2
NUDGE_CHOICES = 71           # nudge 0-70 ticks (about 0-30.4 degrees)
# The original 24-colour palette's ring: one sRGB channel at 250, one at 112.
# Every colour stays on it, so blends travel round the wheel instead of
# through grey. The old palette occurs at multiples of UNITS // 24.
SCRAMBLE_PERIOD = 1 << 64
# The full route's period is lcm(828, 2**64) blends of six words. See the
# repeat-period proof in references/format-recipes.md. Individual short colour
# sequences can recur sooner; the stored position itself never wraps.
PERIOD_BLENDS = TICKS * SCRAMBLE_PERIOD // math.gcd(TICKS, SCRAMBLE_PERIOD)
PERIOD_WORDS = BLEND_WORDS * PERIOD_BLENDS
RAINBOW_HEX = re.compile(r'#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})')


def check_position(value: object, name: str = 'start_index') -> int:
    """Positions are exact non-negative integers; floats, bools and text are refused."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f'{name} must be a whole number 0 or more.')
    return value


def parse_position(text: str, name: str = 'start index') -> int:
    """Strict base-10 digits only: no sign, separator, decimal point or non-ASCII digit."""
    if not re.fullmatch(r'[0-9]+', text):
        raise ValueError(f'The {name} must be a whole number 0 or more, written with digits 0-9 only.')
    return int(text)


def _scramble(number: int) -> int:
    """SplitMix64 finaliser: a fixed, exact integer bijection on number mod 2**64."""
    z = (number % SCRAMBLE_PERIOD + 1) * 0x9E3779B97F4A7C15 % SCRAMBLE_PERIOD
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9 % SCRAMBLE_PERIOD
    z = (z ^ (z >> 27)) * 0x94D049BB133111EB % SCRAMBLE_PERIOD
    return z ^ (z >> 31)


def destination(blend: int) -> int:
    """Hue tick (0-827) where blend number `blend` starts."""
    z = _scramble(check_position(blend, 'blend'))
    return (TURN * blend + HALF_TURN * (z >> 63) + z % NUDGE_CHOICES) % TICKS


def blend_jump(blend: int) -> int:
    """Shortest signed route to the next destination, with no whole-route reverse setting."""
    step = (destination(blend + 1) - destination(blend)) % TICKS
    return step if step < HALF_TURN else step - TICKS


def ring_colour(units: int) -> str:
    """Exact #rrggbb for a hue on the bright ring, rounding halves up like the original palette."""
    sector, offset = divmod(units % UNITS, SECTOR)
    span = BRIGHT - DIM
    rising = DIM + (2 * span * offset + SECTOR) // (2 * SECTOR)
    falling = DIM + (2 * span * (SECTOR - offset) + SECTOR) // (2 * SECTOR)
    red, green, blue = [(BRIGHT, rising, DIM), (falling, BRIGHT, DIM), (DIM, BRIGHT, rising),
                        (DIM, falling, BRIGHT), (rising, DIM, BRIGHT), (BRIGHT, DIM, falling)][sector]
    return f'#{red:02x}{green:02x}{blue:02x}'


def word_colour(position: int) -> str:
    """Colour for one word position: evenly spaced along the current blend."""
    blend, offset = divmod(check_position(position, 'position'), BLEND_WORDS)
    return ring_colour(destination(blend) * BLEND_WORDS + blend_jump(blend) * offset)


def is_rainbow_colour(value: str) -> bool:
    """True for a helper colour: lowercase #rrggbb on the ring (one channel 250, one 112)."""
    match = RAINBOW_HEX.fullmatch(value)
    if not match:
        return False
    channels = [int(part, 16) for part in match.groups()]
    return max(channels) == BRIGHT and min(channels) == DIM


def _state_path() -> Path:
    home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    # The growing word position has its own file. The older
    # rainbow-next-index.txt is still read and rewritten as 0-23 by the previous
    # helper and by Agent Flow's AuthoredTextRainbow.swift; sharing it would pull
    # this route back to its start. That file is left untouched for them.
    return home / 'state' / 'response-preferences' / 'rainbow-next-word.txt'


def reserve_word_positions(word_counts: Iterable[int]) -> list[int]:
    """Reserve a consecutive run of word positions for each quote in one locked update.

    Returns each quote's first position. The saved position only grows.
    """
    counts = list(word_counts)
    if not counts or any(isinstance(count, bool) or not isinstance(count, int) or count < 1 for count in counts):
        raise ValueError('Each quote needs a positive whole number of words.')
    state = _state_path()
    state.parent.mkdir(parents=True, exist_ok=True)
    with state.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            position = parse_position(state.read_text(encoding='utf-8').strip(), 'saved rainbow position')
        except FileNotFoundError:
            position = 0
        except ValueError as error:
            raise ValueError(f'Invalid rainbow counter in {state}; repair it before generating another quote.') from error
        starts = []
        for count in counts:
            starts.append(position)
            position += count
        fd, temporary = tempfile.mkstemp(dir=state.parent, prefix='.rainbow-')
        try:
            with os.fdopen(fd, 'w') as stream:
                stream.write(str(position) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, state)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        return starts


def next_start_index(word_count: int = 1) -> int:
    """Reserve one quote's word positions across tasks; keep runtime state outside the skill."""
    return reserve_word_positions([word_count])[0]


def chunks(text):
    """One colour per whitespace-delimited word."""
    return text.split()


def validate_short_quote(text, claude=False):
    """Reject long reminder excerpts before reserving any word positions."""
    visible = ' '.join(chunks(text))
    if not visible:
        raise ValueError('Provide the relevant question or excerpt as plain text.')
    if claude and len(chunks(text)) > CLAUDE_MAX_WORDS:
        raise ValueError(
            f'Rainbow reminder has {len(chunks(text))} words; Claude desktop shows longer reminders as raw text. '
            f'Choose an exact relevant excerpt of {CLAUDE_MAX_WORDS} words or fewer.'
        )
    if len(visible) > MAX_QUOTE_CHARS:
        raise ValueError(
            f'Rainbow reminder is {len(visible)} characters; choose an exact relevant excerpt '
            f'of {MAX_QUOTE_CHARS} characters or fewer; longer reminders wrap naturally.'
        )
    return visible


def tex(text, claude=False):
    escapes = CLAUDE_ESCAPES if claude else ESCAPES
    return ''.join(escapes.get(char, char) for char in text)


def inline_code(text):
    fence = '`' * (max((len(m[0]) for m in re.finditer(r'`+', text)), default=0) + 1)
    return fence + ' ' + text + ' ' + fence


def render(text, format='markdown', start_index=None, claude=False):
    if not text.strip():
        raise ValueError('Provide the relevant question or excerpt as plain text.')
    words = chunks(text)
    if start_index is None:
        start_index = next_start_index(len(words))
    check_position(start_index)
    parts, expressions, group = [], [], []
    group_chars = 0
    def flush_group():
        nonlocal group_chars
        if not group:
            return
        expression = r'\textsf{' + ' '.join(group) + '}'
        expressions.append(expression)
        parts.append(r'\(' + expression + r'\)')
        group.clear()
        group_chars = 0
    for i, chunk in enumerate(words):
        if len(chunk) > MAX_CHARS:
            # Do not turn a long URL/identifier into an unbreakable math box.
            # It still uses its word position so the blend keeps its spacing.
            if format == 'markdown':
                flush_group()
            parts.append('<code>' + html.escape(chunk) + '</code>' if format == 'html' else inline_code(chunk))
            continue
        colour = word_colour(start_index + i)
        if format == 'html':
            parts.append('<span class="rq-chunk" style="color:' + colour + '">' + html.escape(chunk) + '</span>')
        else:
            needed = len(chunk) + (1 if group else 0)
            if group and group_chars + needed > MAX_GROUP_CHARS:
                flush_group()
            group.append(r'\color{' + colour + '}{' + tex(chunk, claude) + '}')
            group_chars += len(chunk) + (1 if group_chars else 0)
    if format == 'markdown':
        flush_group()
    return ('<span class="rainbow-quote">' + ' '.join(parts) + '</span>' if format == 'html'
            else '> ' + ' '.join(parts)), expressions


def start_index_argument(value):
    try:
        return parse_position(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, nargs='+', help='One or more UTF-8 plain-text question files; never shell-interpolated messages.')
    parser.add_argument('--format', choices=['markdown', 'html'], default='markdown')
    parser.add_argument('--start-index', type=start_index_argument, metavar='N',
                        help='Pin the first word position (any whole number 0 or more) without reading or advancing the counter, '
                             'for reproducible examples/tests. Later files continue where the previous one ended.')
    parser.add_argument('--claude', action='store_true', help='Claude desktop output: at most 8 words, \\textdollar{} for $, and Claude raw-text checks.')
    parser.add_argument('--long-demo', action='store_true',
                        help='Demonstrate the colour route on a long excerpt. Requires --start-index and never touches the counter; '
                             'normal reminders keep their length limits.')
    args = parser.parse_args()
    if args.long_demo and args.start_index is None:
        parser.error('--long-demo needs --start-index so a demonstration never advances the shared counter.')
    if args.long_demo and args.claude:
        # Claude's 200-character expression limit is protected by the 8-word
        # reminder rule; long demos are for Codex Markdown and website HTML.
        parser.error('--long-demo is for Codex Markdown or website HTML, not --claude.')
    try:
        texts = [source.read_text(encoding='utf-8') for source in args.source]
        if any(not text.strip() for text in texts):
            raise ValueError('Provide each relevant question or excerpt as plain text.')
        if args.format == 'markdown' and not args.long_demo:
            texts = [validate_short_quote(text, args.claude) for text in texts]
        counts = [len(chunks(text)) for text in texts]
        if args.start_index is None:
            starts = reserve_word_positions(counts)
        else:
            starts, position = [], args.start_index
            for count in counts:
                starts.append(position)
                position += count
        rendered = [render(text, args.format, start, args.claude) for text, start in zip(texts, starts)]
        outputs = [item[0] for item in rendered]
        expressions = [expression for item in rendered for expression in item[1]]
        spec = importlib.util.spec_from_file_location('quote_math', Path(__file__).with_name('math-validation.py'))
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        errors = [error for error in validator.render_errors(expressions) if error]
        if args.claude:
            errors.extend(validator.claude_raw_errors('\n\n'.join(outputs)))
        if errors:
            parser.exit(1, '\n'.join(errors) + '\n')
        print('\n\n'.join(outputs))
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
