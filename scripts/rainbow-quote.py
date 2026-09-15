#!/usr/bin/env python3
"""Render a literal question reminder using the fixed rainbow recipe."""
import argparse
import html
import importlib.util
from pathlib import Path
import re

PALETTE = ('#fa7070', '#fa9370', '#fab570', '#fad870', '#fafa70', '#d8fa70', '#b5fa70', '#93fa70', '#70fa70', '#70fa93', '#70fab5', '#70fad8', '#70fafa', '#70d8fa', '#70b5fa', '#7093fa', '#7070fa', '#9370fa', '#b570fa', '#d870fa', '#fa70fa', '#fa70d8', '#fa70b5', '#fa7093')
MAX_CHARS = 24
ESCAPES = {'\\': r'\textbackslash{}', '{': r'\{', '}': r'\}', '#': r'\#',
           '%': r'\%', '_': r'\_', '&': r'\&', '$': r'\$',
           '^': r'\textasciicircum{}', '~': r'\textasciitilde{}'}


def chunks(text):
    """One colour per whitespace-delimited word, continuing across line wraps."""
    return text.split()


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
