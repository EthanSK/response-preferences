import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('live_viewer', ROOT / 'scripts/live-viewer.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


class LiveViewerTests(unittest.TestCase):
    def test_range_links_use_the_same_registered_source_and_reject_invalid_bounds(self):
        self.file.write_text('one\ntwo\nthree\n')
        with patch.object(live, 'ensure_server'), patch.object(live, 'register', return_value=self.key):
            self.assertTrue(live.open_viewer(self.file, 2, 3).endswith('#L2-L3'))
            self.assertTrue(live.open_viewer(self.file, 2).endswith('#L2'))
            for start, end in [(None, 2), (3, 2), (1, 99)]:
                with self.assertRaises(ValueError): live.open_viewer(self.file, start, end)
        self.assertEqual(self.file.read_text(), 'one\ntwo\nthree\n')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.state = self.root / 'state'
        self.file = self.root / 'original.md'
        self.file.write_text('# Original\n')
        self.key = live.register(self.file, self.state)
        self.server = live.ViewerServer(('127.0.0.1', 0), self.state)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = 'http://127.0.0.1:%d' % self.server.server_port

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join(); self.temp.cleanup()

    def request(self, suffix=None, body=None, headers=None):
        suffix = suffix or '/api/document?doc=' + self.key
        headers = headers or {}
        if body is not None:
            body = json.dumps(body).encode()
            headers = {'Content-Type': 'application/json', 'X-Viewer-Document': self.key, **headers}
        try:
            with urlopen(Request(self.base + suffix, body, headers), timeout=3) as response:
                return response.status, response.read()
        except HTTPError as error:
            with error: return error.code, error.read()

    def test_same_link_reads_current_source_and_shell_contains_no_document(self):
        shell = self.request('/index.html?doc=' + self.key)[1].decode()
        self.assertNotIn('# Original', shell)
        first = json.loads(self.request()[1])
        self.file.write_text('# Changed externally\n')
        second = json.loads(self.request()[1])
        self.assertEqual(second['source'], self.file.read_text())
        self.assertNotEqual(first['revision'], second['revision'])
        self.assertEqual(live.register(self.file, self.state), self.key)

    def test_prompt_preview_uses_the_current_archive_and_reveals_exact_file(self):
        self.file.write_text(
            '<!-- Agent Flow rainbow start: 6 -->\n<!-- Agent Flow: reminder -->\n\n'
            '<speech>Ask &amp; answer</speech>\n\n'
            '<app_selection><text>&lt;script&gt;</text></app_selection>\n\n'
            '## Agent Flow interpretation guidance for this prompt\n\n<speech>Appendix only</speech>\n'
        )
        name = 'prompt-00000000-0000-0000-0000-000000000000-11111111-1111-1111-1111-111111111111.md'
        route = '?prompt=' + name
        with patch.object(live.agent_flow_prompt, 'archive_path', return_value=self.file):
            status, body = self.request('/api/document' + route)
            self.assertEqual(status, 200)
            response = json.loads(body)
            self.assertEqual(response['source'], self.file.read_text())
            self.assertEqual(response['prompt']['rainbow'], 6)
            self.assertEqual([e['text'] for e in response['prompt']['events']], ['Ask & answer', '<script>'])
            headers = {'X-Viewer-Document': name}
            self.assertEqual(self.request('/api/document' + route, {}, headers)[0], 404)
            self.assertEqual(self.request('/api/reveal' + route, {}, {'Origin': 'https://example.org', **headers})[0], 403)
            with patch.object(live.sys, 'platform', 'darwin'), patch.object(live.subprocess, 'run') as run:
                self.assertEqual(self.request('/api/reveal' + route, {}, headers)[0], 200)
                run.assert_called_once_with(['/usr/bin/open', '-R', str(self.file)], check=True, timeout=5)

    def test_save_original_and_reject_stale_save_without_destroying_external_work(self):
        original = json.loads(self.request()[1])
        self.assertEqual(self.request(body={'revision': original['revision'], 'source': '# Saved\n'})[0], 200)
        self.assertEqual(self.file.read_text(), '# Saved\n')
        self.file.write_text('# External\n')
        self.assertEqual(self.request(body={'revision': original['revision'], 'source': '# Stale draft\n'})[0], 409)
        self.assertEqual(self.file.read_text(), '# External\n')

    def test_prompt_preview_lists_guidance_below_the_timeline(self):
        text = (
            '<typed_text>My question</typed_text>\n\n'
            '## Response preferences for this reply\n\n'
            'Use the full skill.\n\n<speech>Example inside the skill</speech>\n'
        )
        preview = live.agent_flow_prompt.timeline(text)
        self.assertEqual([event['text'] for event in preview['events']], ['My question'])
        self.assertEqual(preview['guidance'], [{
            'label': 'Response Preferences',
            'text': 'Use the full skill.\n\n<speech>Example inside the skill</speech>',
        }])
        both = text.replace('## Response preferences', (
            '## Agent Flow interpretation guidance for this prompt\n\n'
            'Keep my selection in context.\n\n## Response preferences'
        ))
        preview = live.agent_flow_prompt.timeline(both)
        self.assertEqual([item['label'] for item in preview['guidance']],
                         ['Agent Flow interpretation', 'Response Preferences'])
        self.assertEqual(preview['guidance'][0]['text'], 'Keep my selection in context.')

    def test_denies_unregistered_paths_cross_origin_writes_and_symlink_replacement(self):
        self.assertEqual(self.request('/api/document?doc=unknown&path=' + str(self.file))[0], 403)
        original = json.loads(self.request()[1])
        payload = {'source': '# Bad\n', 'revision': original['revision']}
        self.assertEqual(self.request(body=payload, headers={'Origin': 'https://example.invalid'})[0], 403)
        self.assertEqual(self.request(body=payload, headers={'X-Viewer-Document': ''})[0], 403)
        other = self.root / 'private.md'; other.write_text('private')
        self.file.unlink(); self.file.symlink_to(other)
        self.assertEqual(self.request()[0], 400)
        self.assertEqual(self.request(body=payload)[0], 400)
        self.assertEqual(other.read_text(), 'private')

    def test_missing_file_is_explicit_error_and_new_link_cannot_expand_access(self):
        other = self.root / 'other.md'; other.write_text('not registered')
        self.file.write_text('[Other](other.md)')
        current = json.loads(self.request()[1])
        self.assertEqual(current['links'], {})
        self.file.unlink()
        self.assertEqual(self.request()[0], 400)


if __name__ == '__main__': unittest.main()
