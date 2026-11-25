"""Check snapshot exports and file-allocation limits without large fixtures."""
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import Mock, patch

spec=importlib.util.spec_from_file_location('generator', Path(__file__).resolve().parents[1] / 'scripts/create-viewer.py')
generator=importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class GeneratorTests(unittest.TestCase):
    def test_growing_file_read_is_bounded_before_rejection(self):
        # A stale size check must never turn into an unbounded allocation.
        reads = []
        class GrowingFile(BytesIO):
            def read(self, size=-1):
                reads.append(size)
                self.assert_bounded(size)
                return super().read(size)

            @staticmethod
            def assert_bounded(size):
                if size != 33:
                    raise AssertionError('Read must request only the limit plus one byte')

        path = Mock()
        path.stat.return_value.st_size = 1
        path.open.return_value = GrowingFile(b'x' * 100)
        with self.assertRaisesRegex(ValueError, 'too large'):
            generator.read_bounded(path, 32, 'too large')
        self.assertEqual(reads, [33])

    def test_bounded_read_accepts_exact_limit_and_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'text.txt'
            path.write_bytes(b'\xef\xbb\xbfhi\r\n')
            self.assertEqual(generator.read_bounded(path, 7, 'too large'), path.read_bytes())

    def test_snapshot_images_respect_actual_remaining_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'images.md'
            image = Path(tmp) / 'image.png'
            source.write_text('![Image](image.png)\n')
            image.write_bytes(b'short')
            bounded = generator.read_bounded
            def grow_image(path, limit, error):
                if path == image.resolve():
                    path.write_bytes(b'x' * 20)
                return bounded(path, limit, error)
            with patch.object(generator, 'MAX_IMAGES', 10), patch.object(generator, 'read_bounded', side_effect=grow_image):
                page = generator.create_viewer(source, Path(tmp) / 'snapshot.html').read_text()
            payload = json.loads(re.search(r'<script id="document-data" type="application/json">(.*?)</script>', page, re.S).group(1))
            self.assertEqual(payload['images'], {})

    def test_code_range_is_retained_in_snapshot_without_changing_the_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'example.ts';source.write_text('one\ntwo\nthree\n')
            page=generator.create_viewer(source,Path(tmp)/'range.html',2,end_line=3).read_text()
            payload=json.loads(re.search(r'<script id="document-data" type="application/json">(.*?)</script>',page,re.S).group(1))
            self.assertEqual((payload['line'],payload['endLine']),(2,3))
            self.assertEqual(source.read_text(),'one\ntwo\nthree\n')
            with self.assertRaises(ValueError):generator.create_viewer(source,Path(tmp)/'invalid.html',3,end_line=2)

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
