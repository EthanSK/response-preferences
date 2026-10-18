#!/usr/bin/env python3
"""Build hover-only Markdown links without changing the source words."""
import argparse
from pathlib import Path
import re
import sys
import unicodedata


def hover_link(text):
    if not text.strip() or any(unicodedata.category(c) in ('Cc', 'Cs', 'Zl', 'Zp') for c in text):
        raise ValueError('Use a real context viewer for empty, multiline or control-character text; do not strip it.')
    # Preserve literal URL escapes and keep the whole source in the path,
    # including a leading slash, query punctuation and fragments.
    target = text.replace('%', '%25').replace('/', '%2F').replace('?', '%3F').replace('#', '%23').replace(' ', '%20')
    # CommonMark angle destinations still require escaped internal brackets.
    # Escape ampersands too so source such as &copy; is not decoded as an entity.
    target = re.sub(r'[\\<>&]', lambda m: '\\' + m.group(), target)
    return '[↗](</' + target + '>)'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', help='UTF-8 source text files; - reads standard input')
    args = parser.parse_args()
    try:
        links = [hover_link(sys.stdin.read() if f == '-' else Path(f).read_text(encoding='utf-8')) for f in args.files]
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, str(error) + '\n')
    print('\n'.join(links))


if __name__ == '__main__':
    main()
