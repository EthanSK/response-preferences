"""Parse Agent Flow's canonical prompt for the shared viewer, without copying the archive."""

from pathlib import Path
import re
from urllib.parse import unquote
from xml.etree import ElementTree


PROMPT_DIRECTORY = Path.home() / 'Library/Application Support/AgentFlow/Prompts'
UUID = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
PROMPT_NAME = re.compile(rf'prompt-{UUID}-{UUID}\.md')
FRAGMENT = re.compile(
    r'^[\t ]*<(speech|speech_segment|typed_text|potential_tts|app_selection|codex_selection)\b[^>]*>.*?</\1>'
    r'|^[\t ]*<(?:local_screenshot|app_selection_image)\b[^>]*?/>',
    re.MULTILINE | re.DOTALL,
)
IMAGES = {'local_screenshot', 'app_selection_image'}
GUIDANCE_LABELS = {
    'Agent Flow interpretation guidance for this prompt': 'Agent Flow interpretation',
    'Response preferences for this reply': 'Response Preferences',
}
GUIDANCE_HEADING = re.compile(
    r'(?:\A|\n\n)## (' + '|'.join(map(re.escape, GUIDANCE_LABELS)) + r')[\t ]*(?:\n|\Z)'
)


def archive_path(name: str, directory: Path = PROMPT_DIRECTORY) -> Path:
    if not PROMPT_NAME.fullmatch(name):
        raise PermissionError('Invalid Agent Flow prompt.')
    path = directory / name
    if directory.is_symlink() or path.is_symlink() or not path.is_file():
        raise FileNotFoundError('The original Agent Flow prompt is unavailable.')
    return path


def timeline(source: str) -> dict:
    start = re.match(r'<!-- Agent Flow rainbow start: (\d{1,18}) -->\s*', source)
    rainbow = int(start[1]) if start else 0
    source = source[start.end():] if start else source
    source = re.sub(r'\A(?:<!-- Agent Flow:[^\n]* -->\s*)+', '', source)
    events = []
    end = 0
    preceding_image = None

    def plain(text: str) -> None:
        text = text.strip()
        if preceding_image and text.startswith('![Screenshot](<'):
            line, _, remainder = text.partition('\n')
            if line.endswith('>)') and unquote(line[len('![Screenshot](<'):-2]) == preceding_image:
                text = remainder.strip()
        if text:
            events.append({'kind': 'text', 'text': text, 'attributes': {}})

    for match in FRAGMENT.finditer(source):
        # The optional skill is an appendix, not part of the captured timeline.
        intervening = source[end:match.start()]
        if GUIDANCE_HEADING.search(intervening):
            break
        plain(intervening)
        preceding_image = None
        fragment = match[0].lstrip()
        try:
            if re.search(r'<!DOCTYPE|<!ENTITY', fragment, re.IGNORECASE):
                raise ValueError('Declarations are not prompt events')
            node = ElementTree.fromstring(fragment)
            if node.tag in IMAGES and (len(node) or (node.text or '').strip()):
                raise ValueError('Image events have no payload')
            if node.tag in ('app_selection', 'codex_selection'):
                if len(node) != 1 or node[0].tag != 'text' or len(node[0]):
                    raise ValueError('Invalid selection')
                text = node[0].text or ''
            else:
                if len(node):
                    raise ValueError('Invalid event payload')
                text = node.text or ''
            if node.tag in IMAGES:
                preceding_image = node.attrib.get('path')
            events.append({'kind': node.tag, 'text': text, 'attributes': node.attrib})
        except (ElementTree.ParseError, ValueError):
            plain(fragment)
        end = match.end()
    tail = source[end:]
    headings = list(GUIDANCE_HEADING.finditer(tail))
    plain(tail[:headings[0].start()] if headings else tail)
    guidance = [
        {'label': GUIDANCE_LABELS[heading[1]], 'text': tail[heading.end():end].strip('\n')}
        for heading, end in zip(headings, [item.start() for item in headings[1:]] + [len(tail)])
    ]
    return {'events': events, 'rainbow': rainbow, 'guidance': guidance}
