#!/usr/bin/env python3
"""Derive public rainbow colours from the helper, then rebuild viewer exports.

Called by npm run build. Question wording remains in the HTML/SVG sources;
their colour attributes are generated here so examples cannot drift from the
same formula used by installed replies. No runtime counter is read or written.
"""
import importlib.util
from pathlib import Path
import html
import re

root=Path(__file__).resolve().parents[1]
rainbow_spec=importlib.util.spec_from_file_location('demo_rainbow',root/'scripts/rainbow-quote.py')
rainbow=importlib.util.module_from_spec(rainbow_spec)
rainbow_spec.loader.exec_module(rainbow)

def recolour_questions(source: str) -> str:
    """Recolour the supported generated word-span/code shape, preserving wording."""
    position=0
    pattern=r'<span class="rainbow-quote">((?:<span class="rq-chunk"[^>]*>[^<]*</span>|<code>[^<]*</code>|\s)*)</span>'
    def replace(match):
        nonlocal position
        text=html.unescape(re.sub(r'<[^>]+>','',match[1]))
        rendered,_=rainbow.render(text,'html',start_index=position)
        position+=len(text.split())
        return rendered
    updated,count=re.subn(pattern,replace,source)
    if count != source.count('<span class="rainbow-quote">'):
        raise ValueError('An unsupported rainbow question shape needs explicit handling.')
    return updated

homepage=root/'docs/index.html'
homepage.write_text(recolour_questions(homepage.read_text(encoding='utf-8')),encoding='utf-8')
poster=root/'docs/readme-preview.svg'
poster_source=poster.read_text(encoding='utf-8')
def recolour_poster(match):
    position=0
    def word(span):
        nonlocal position
        colour=rainbow.word_colour(position)
        position+=1
        return span[1]+colour+span[2]
    body=re.sub(r'(<tspan\b[^>]*\bfill=")#[0-9a-f]{6}("[^>]*>)',word,match[2])
    return match[1]+body+match[3]
poster.write_text(re.sub(r'(<text\b[^>]*\bclass="rainbow-preview"[^>]*>)(.*?)(</text>)',recolour_poster,poster_source),encoding='utf-8')

spec=importlib.util.spec_from_file_location('viewer', root/'scripts/create-viewer.py')
viewer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(viewer)
for source,output,line in [('docs/example.md','docs/viewer.html',9),('docs/message.md','docs/message.html',1),('SKILL.md','docs/skill.html',1),('docs/format-message.md','docs/format-message.html',1)]:
    target=root/output
    if target.exists(): target.unlink()
    print(viewer.create_viewer(root/source,target,line,public=True))
