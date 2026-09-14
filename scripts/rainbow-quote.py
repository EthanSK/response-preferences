#!/usr/bin/env python3
"""Render a literal question reminder using the fixed rainbow recipe."""
import argparse
import html
import importlib.util
import math
from pathlib import Path
import re

PALETTE = ('#f87171', '#fb923c', '#facc15', '#4ade80', '#22d3ee', '#60a5fa', '#c084fc')
MAX_CHARS = 24
ESCAPES = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '#': r'\#',
           '%': r'\%', '_': r'\_', '&': r'\&', '$': r'\$',
           '^': r'\textasciicircum{}', '~': r'\textasciitilde{}'}


def chunks(text):
    """Keep word order; short quotes change colour faster, long ones use phrases."""
    words = text.split()
    if not words:
        return []
    # Spread even a medium-length quote across the full palette without adding
    # per-letter wrappers. Longer quotes keep the same three-word upper bound.
    count = min(len(words), max(len(PALETTE), math.ceil(len(words) / 3)))
    size, extra = divmod(len(words), count)
    result, offset = [], 0
    for group in range(count):
        width = size + (group < extra)
        current = []
        for word in words[offset:offset + width]:
            if current and len(' '.join(current + [word])) > MAX_CHARS:
                result.append(' '.join(current))
                current = []
            current.append(word)
        result.append(' '.join(current))
        offset += width
    return result


def tex(text):
    return ''.join(ESCAPES.get(char, char) for char in text)


def inline_code(text):
    fence = '`' * (max((len(m[0]) for m in re.finditer(r'`+', text)), default=0) + 1)
    return fence + ' ' + text + ' ' + fence


def render(text, format='markdown'):
    if not text.strip():
        raise ValueError('Provide the relevant question or excerpt as plain text.')
    parts, expressions = [], []
    for i, chunk in enumerate(chunks(text)):
        if len(chunk) > MAX_CHARS:
            # Do not turn a long URL/identifier into an unbreakable math box.
            parts.append('<code>' + html.escape(chunk) + '</code>' if format == 'html' else inline_code(chunk))
            continue
        colour = PALETTE[i % len(PALETTE)]
        expression = r'\color{' + colour + r'}{\textsf{' + tex(chunk) + '}}'
        expressions.append(expression)
        parts.append('<span class="rq-chunk" style="color:' + colour + '">' + html.escape(chunk) + '</span>'
                     if format == 'html' else r'\(' + expression + r'\)')
    return ('<span class="rainbow-quote">' + ' '.join(parts) + '</span>' if format == 'html'
            else '> ' + ' '.join(parts)), expressions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='UTF-8 plain-text question file; never a shell-interpolated message.')
    parser.add_argument('--format', choices=['markdown', 'html'], default='markdown')
    args = parser.parse_args()
    try:
        output, expressions = render(args.source.read_text(encoding='utf-8'), args.format)
        spec = importlib.util.spec_from_file_location('quote_math', Path(__file__).with_name('math-validation.py'))
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        errors = [error for error in validator.render_errors(expressions) if error]
        if errors:
            parser.exit(1, '\n'.join(errors) + '\n')
        print(output)
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
