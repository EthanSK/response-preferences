import importlib.util
from pathlib import Path
import subprocess
import sys
import json
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('guard', ROOT/'scripts/guard-reply.py')
guard = importlib.util.module_from_spec(spec); spec.loader.exec_module(guard)
GOOD = r'\(\huge\text{👉}\) The \(\underline{\textsf{export keeps every final frame}}\).' + '\n\n' + r'\(\color{#b8a4d9}{\textsf{About: the export fix.}}\)'

class GuardTests(unittest.TestCase):
    def test_completion_guard_catches_percent_renderer_failure(self):
        broken = GOOD.replace('export keeps every final frame','matching list covers about 54%')
        self.assertTrue(any('percent' in e for e in guard.errors_for(broken)))
        self.assertEqual([],guard.errors_for(broken.replace('%',r'\%')))

    def test_explicit_plain_text_and_yaml_exceptions_are_task_and_reply_bound(self):
        session = '01a07780-aa0b-7352-b2dc-44a38a666d42'
        other = '01a071d2-bfc5-7151-ac5a-30ebf54dd7aa'
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            for text in ['one two three four five', 'name: sample\nstatus: ready\n']:
                self.assertTrue(guard.errors_for(text))
                draft = home / 'reply.txt'; draft.write_text(text)
                payload = home / 'payload.json'
                payload.write_text(json.dumps({'reply_file': str(draft), 'session_id': session, 'reason': 'explicit_user_format', 'request': 'Return only the requested text, without commentary.'}))
                import os
                result = subprocess.run([sys.executable, str(ROOT/'scripts/exempt-reply.py'), str(payload)], env={**os.environ, 'CODEX_HOME': tmp}, capture_output=True, text=True, check=True)
                self.assertTrue(json.loads(result.stdout)['prepared'])
                self.assertTrue(guard.is_exempt(home, session, text))
                self.assertFalse(guard.is_exempt(home, other, text))
                self.assertFalse(guard.is_exempt(home, session, text+'changed'))
                path = guard.exemption_path(home, session, text)
                self.assertEqual(0o600, path.stat().st_mode & 0o777)
                path.write_text('{broken')
                self.assertFalse(guard.is_exempt(home, session, text))
    def test_omitted_format_is_caught_even_without_explicit_draft_check(self):
        errors = guard.errors_for('Did you mean the saved file or the exported copy?')
        self.assertTrue(any('🫵' in e for e in errors))
        self.assertTrue(any('About:' in e for e in errors))
        self.assertTrue(any('underlined' in e for e in errors))
    def test_valid_correction_and_transport_citation_pass(self):
        self.assertEqual([], guard.errors_for(GOOD))
        self.assertEqual([], guard.errors_for(GOOD+'\n<oai-mem-citation>data</oai-mem-citation>'))
    def test_quotes_do_not_supply_underlines_or_fingers(self):
        self.assertTrue(guard.errors_for('> '+GOOD+'\n\nPlease identify which copy you mean.'))
    def test_empty_and_structured_artifacts_are_left_alone(self):
        for text in [None, '', '{}', '[1,2]', '```json\n{"ok":true}\n```', '> Exact original words']:
            self.assertEqual([], guard.errors_for(text), text)
    def test_code_fence_with_prose_still_checks_prose(self):
        self.assertTrue(guard.errors_for('Here is the requested configuration.\n```json\n{}\n```'))
    def test_real_paths_and_project_extensions_are_not_guessed_by_hook(self):
        project = r'\(\huge\text{🧬}\) '+r'\(\huge\text{👉}\) The \(\underline{\textsf{sample is ready}}\).'+'\n\n'+GOOD.split('\n\n')[1]
        self.assertEqual([],guard.errors_for(project))
        self.assertEqual([],guard.errors_for(GOOD.replace('The ', 'The [sample](/missing-file.html) ',1)))
    def test_cli_requests_one_repair_and_never_loops(self):
        for active in [False, True]:
            p=subprocess.run([sys.executable,str(ROOT/'scripts/guard-reply.py')],input=json.dumps({'last_assistant_message':'Which file did you mean?', 'stop_hook_active':active}),text=True,capture_output=True,check=True)
            out=json.loads(p.stdout)
            self.assertEqual('decision' in out,not active)
            self.assertIn('ORIGINAL user request',out['additionalContext'])
            self.assertIn('Do not rerun domain work',out['additionalContext'])
