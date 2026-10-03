import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('generator', Path(__file__).resolve().parents[1] / 'scripts/create-viewer.py')
generator=importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class GeneratorTests(unittest.TestCase):
    def test_appearance_is_whitelisted_private_and_changes_snapshot_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp); source=home/'theme.md';source.write_text('# Theme\n')
            config=home/'config.toml'
            config.write_text('''[desktop]
appearanceTheme = "dark"
appearanceDarkCodeThemeId = "linear"
unrelatedSecret = "must never appear"
[desktop.appearanceDarkChromeTheme]
surface = "#0f0f11"
ink = "#e3e4e6"
accent = "#606acc"
contrast = 50
[desktop.appearanceDarkChromeTheme.fonts]
ui = "Inter"
code = "bad; background:red"
''')
            with patch.dict('os.environ',{'CODEX_HOME':tmp}):
                first=generator.create_viewer(source)
                page=first.read_text()
                payload=json.loads(re.search(r'<script id="document-data" type="application/json">(.*?)</script>',page,re.S).group(1))
                self.assertEqual(payload['appearance']['mode'],'dark')
                self.assertEqual(payload['appearance']['dark']['ui'],'Inter')
                self.assertEqual(payload['appearance']['dark']['codeThemeId'],'linear')
                self.assertNotIn('code',payload['appearance']['dark'])
                self.assertNotIn('must never appear',page)
                config.write_text(config.read_text().replace('#606acc','#12abcd'))
                second=generator.create_viewer(source)
                self.assertNotEqual(first,second)
                public=generator.create_viewer(source,home/'public.html',public=True).read_text()
                payload=json.loads(re.search(r'<script id="document-data" type="application/json">(.*?)</script>',public,re.S).group(1))
                self.assertNotIn('appearance',payload)
                config.write_text('[desktop.appearanceDarkChromeTheme]\nsurface = "red; url(bad)"\n')
                self.assertEqual(generator.codex_appearance(),{})

    def test_exact_source_roundtrip_and_script_termination(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'test.md';text='# Test\r\n\r\n</script><script>alert(1)</script>\r\n';source.write_bytes(text.encode())
            output=generator.create_viewer(source,Path(tmp)/'out.html',3)
            page=output.read_text();payload=re.search(r'<script id="document-data" type="application/json">(.*?)</script>',page,re.S).group(1)
            self.assertEqual(json.loads(payload)['source'],text)
            self.assertNotIn('</script>',payload)
            self.assertEqual(source.read_bytes(),text.encode())
            self.assertNotIn('__NONCE__',page)
            with self.assertRaises(FileExistsError):generator.create_viewer(source,output)

    def test_image_copy_public_mode_and_invalid_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            image=Path(tmp)/'a b.png';image.write_bytes(b'example bytes')
            source=Path(tmp)/'test.md';source.write_text('![Image](<a b.png>)\n')
            local=generator.create_viewer(source,Path(tmp)/'local.html').read_text()
            self.assertIn('data:image/png;base64,',local)
            public=generator.create_viewer(source,Path(tmp)/'public.html',public=True).read_text()
            payload=json.loads(re.search(r'<script id="document-data" type="application/json">(.*?)</script>',public,re.S).group(1))
            self.assertEqual(payload['images'],{})
            self.assertEqual(payload['links'],{})
            with self.assertRaises(ValueError):generator.create_viewer(source,Path(tmp)/'invalid.html',99)

    def test_rejects_binary_or_overwriting_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source.html';source.write_text('hello')
            with self.assertRaises(ValueError):generator.create_viewer(source,source)
            source.write_bytes(b'\0data')
            with self.assertRaises(ValueError):generator.create_viewer(source,Path(tmp)/'out.html')


if __name__=='__main__':unittest.main()
