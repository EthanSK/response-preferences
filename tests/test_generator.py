import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('generator', Path(__file__).resolve().parents[1] / 'scripts/create-viewer.py')
generator=importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


class GeneratorTests(unittest.TestCase):
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
