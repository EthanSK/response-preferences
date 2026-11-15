import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('context',ROOT/'scripts/create-reply-context.py')
context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context)
class ContextAndDemos(unittest.TestCase):
    def test_public_rainbows_match_the_installed_generator_formula(self):
        rainbow_spec=importlib.util.spec_from_file_location('public_rainbow',ROOT/'scripts/rainbow-quote.py')
        rainbow=importlib.util.module_from_spec(rainbow_spec);rainbow_spec.loader.exec_module(rainbow)
        page=(ROOT/'docs/index.html').read_text()
        spans=re.findall(r'<span class="rq-chunk" style="color:(#[0-9a-f]{6})">[^<]*</span>',page)
        self.assertTrue(spans)
        self.assertEqual([rainbow.word_colour(i) for i in range(len(spans))],spans,
                         'Build must derive every website question from the canonical colour formula')
        poster=(ROOT/'docs/readme-preview.svg').read_text()
        question=re.search(r'class="rainbow-preview">(.*?)</text>',poster).group(1)
        colours=re.findall(r'<tspan fill="(#[0-9a-f]{6})">',question)
        self.assertTrue(colours)
        self.assertEqual([rainbow.word_colour(i) for i in range(len(colours))],colours)

    def test_context_keeps_exact_message_and_image_after_original_expires(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);image=root/'clipboard.png';image.write_bytes(b'image bytes')
            text='Can you check my change?\n\nI mean this exact bit, not the rest.'
            source=root/'input.json';source.write_text(json.dumps({'text':text,'images':[str(image),str(root/'gone.png')]}))
            output=context.create_context(source,root/'message.md');image.unlink()
            document=output.read_text();self.assertTrue(document.startswith('# Your message\n'));self.assertIn(text,document)
            self.assertIn('no longer available',document)
            copied=Path(re.search(r'!\[Attached image 1\]\(<(.+)>\)',document).group(1));self.assertEqual(copied.read_bytes(),b'image bytes')
            with self.assertRaises(FileExistsError):context.create_context(source,output)
    def test_public_viewers_embed_current_sources_not_stale_preferences(self):
        for source,target in [('SKILL.md','docs/skill.html'),('docs/message.md','docs/message.html'),('docs/format-message.md','docs/format-message.html'),('docs/example.md','docs/viewer.html')]:
            with self.subTest(source=source):
                page=(ROOT/target).read_text();payload=json.loads(re.search(r'<script id="document-data" type="application/json">(.*?)</script>',page,re.S).group(1))
                self.assertEqual(payload['source'],(ROOT/source).read_text())
                self.assertEqual(payload['images'],{})
                self.assertEqual(payload['links'],{})
