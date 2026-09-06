#!/usr/bin/env python3
"""Create a private, self-contained document viewer. Python standard library only."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import re
import secrets
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
MAX_TEXT = 5 * 1024 * 1024
MAX_IMAGES = 40 * 1024 * 1024
MIMES = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp'}


def destinations(text):
    # Best effort for inline and reference destinations, including paths in <...>.
    for match in re.finditer(r'!?\[[^\]\n]*\]\(\s*(?:<([^>\n]+)>|([^\s)]+))(?:\s+[^)]*)?\)', text):
        yield match.group(1) or match.group(2)
    for match in re.finditer(r'^\s{0,3}\[[^\]\n]+\]:\s*(?:<([^>\n]+)>|(\S+))', text, re.M):
        yield match.group(1) or match.group(2)


def create_viewer(source, output=None, line=1, embed_images=True, public=False):
    source = Path(source).expanduser().resolve(strict=True)
    if source.stat().st_size > MAX_TEXT:
        raise ValueError('File exceeds the 5 MB text limit')
    raw = source.read_bytes()
    if len(raw) > MAX_TEXT:
        raise ValueError('File exceeds the 5 MB text limit')
    text = raw.decode('utf-8')
    if '\0' in text:
        raise ValueError('Only UTF-8 text files are supported')
    count = len(text.replace('\r\n', '\n').replace('\r', '\n').split('\n'))
    if not 1 <= line <= count:
        raise ValueError(f'Line must be between 1 and {count}')
    template = (ROOT / 'assets/viewer.html').read_text(encoding='utf-8')
    data = {'name': source.name, 'source': text, 'line': line, 'generated': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'), 'images': {}, 'links': {}}
    used = 0
    for href in dict.fromkeys(destinations(text)):
        parsed = urlparse(href)
        if parsed.scheme in ('https', 'http', 'mailto') or href.startswith('#'):
            continue
        if public or parsed.scheme not in ('', 'file') or parsed.netloc:
            continue
        linked = Path(unquote(parsed.path)).expanduser()
        if not linked.is_absolute():
            linked = source.parent / linked
        linked = linked.resolve()
        # Do not fetch remote resources. Existing local text destinations remain ordinary links.
        if linked.is_file():
            data['links'][href] = linked.as_uri() + ('#' + parsed.fragment if parsed.fragment else '')
            mime = MIMES.get(linked.suffix.lower())
            size = linked.stat().st_size
            if embed_images and mime and size <= 20 * 1024 * 1024 and used + size <= MAX_IMAGES:
                image_bytes = linked.read_bytes()
                data['images'][href] = f'data:{mime};base64,' + base64.b64encode(image_bytes).decode('ascii')
                used += len(image_bytes)
    payload = json.dumps(data, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    fingerprint = hashlib.sha256(str(source).encode() + raw + template.encode() + str(line).encode() + json.dumps(data['images'], sort_keys=True).encode() + str(public).encode()).hexdigest()[:16]
    if output is None:
        codex = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex'))
        folder = codex / 'outputs' / 'viewers' / datetime.now().strftime('%Y-%m-%d')
        output = folder / f'{source.stem}-{fingerprint}-L{line}.html'
        if output.exists():
            return output.resolve()
    output = Path(output).expanduser().resolve()
    if output == source or output.suffix.lower() != '.html':
        raise ValueError('Choose a separate .html output')
    if output.exists():
        raise FileExistsError(output)
    page = template.replace('__TITLE__', html.escape(source.name)).replace('__NONCE__', secrets.token_urlsafe(24)).replace('__DOCUMENT__', payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as file:
        file.write(page)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--output')
    parser.add_argument('--line', type=int, default=1)
    parser.add_argument('--no-images', action='store_true')
    parser.add_argument('--public', action='store_true', help='Do not embed local links or images; source text must already be suitable for publication')
    args = parser.parse_args()
    print(create_viewer(args.source, args.output, args.line, not args.no_images, args.public))
