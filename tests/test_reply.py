import importlib.util
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('reply',Path(__file__).resolve().parents[1]/'scripts/check-reply.py')
reply=importlib.util.module_from_spec(spec);spec.loader.exec_module(reply)
class ReplyChecks(unittest.TestCase):
    def test_historical_plain_skill_announcement_is_rejected(self):
        self.assertTrue(reply.check(r'\(\huge\text{🎯}\) Skill use: browser-test-on-macbook and use-macbook-display — open the site.'))
    def test_each_coloured_skill_requires_its_own_existing_link(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'skill.html';p.write_text('example')
            good=rf'\(\huge\text{{🎯}}\) **Skill use:** \(\color{{magenta}}{{\textrm{{skill-creator}}}}\) [↗]({p}) — update the skill.'
            self.assertEqual([],reply.check(good))
            self.assertTrue(reply.check(good.replace(f'[↗]({p})','')))
            p.unlink();self.assertTrue(reply.check(good))
    def test_regressed_marker_and_colour_patterns_are_rejected(self):
        for draft in [r'\(\Huge\text{✅}\) Done.',r'Done. \(\huge\text{✅}\)',r'\(\huge\text{🧠}\) Explanation.',r'\(\huge\text{➕}\) Added.',r'\(\color{gray}{\textsf{A fact}}\)',r'\(\color{magenta}{\textsf{skill-creator}}\)']:
            with self.subTest(draft=draft):self.assertTrue(reply.check(draft))
    def test_quotes_and_code_examples_do_not_become_new_instructions(self):
        self.assertEqual([],reply.check('> Earlier response: '+r'\(\Huge\text{🧠}\)'+'\n\n```md\n<!-- example -->\n```'))
    def test_direct_answer_needs_its_question_quote(self):
        answer=r'\(\huge\text{⮑}\) The quote line is restored.'
        self.assertTrue(reply.check(answer))
        self.assertEqual([],reply.check('> Bring back the quotes.\n\n'+answer))
    def test_colour_cannot_be_a_link_label(self):
        self.assertTrue(reply.check(r'[\(\color{#22c55e}{\textsf{Saved}}\)](/tmp/file.html)',False))
    def test_inline_information_and_multi_block_sections_are_valid(self):
        self.assertEqual([],reply.check(r'\(\huge\text{✅}\) '+r'\(\color{#22c55e}{\textsf{Saved.}}\)'+'\n\n'+r'\(\huge\text{ⓘ}\) '+reply.CARET+'\n\nFirst fact.\n\nSecond fact.'))
    def test_silent_preference_use_needs_no_announcement(self):
        self.assertEqual([],reply.check(r'\(\huge\text{ⓘ}\) This is an explanation.'))
    def test_metadata_and_old_markdown_links_are_rejected(self):
        for draft in ['<!-- codex-notification {} -->','[↗](/tmp/SKILL.md)','[open](/tmp/skill.html)']:
            self.assertTrue(reply.check(draft,False))

    def test_standalone_caret_does_not_leak_to_inline_markers(self):
        self.assertTrue(reply.check(r'\(\huge\text{ⓘ}\)'+'\n\nDetails below.'))
        self.assertEqual([],reply.check(r'\(\huge\text{ⓘ}\) '+reply.CARET+'\n\nDetails below.'))
        self.assertTrue(reply.check(r'\(\huge\text{✅}\) ▾ Saved.'))
        self.assertTrue(reply.check(r'\(\huge\text{✅}\) '+reply.CARET+' Saved.'))
        self.assertEqual([],reply.check(r'\(\huge\text{✅}\) Saved.'))

    def test_answer_stays_inline_before_supporting_blocks(self):
        for block in ['| Item | Status |\n|---|---|\n| Copy | Done |', '- First item\n- Second item', '```text\nexample\n```', 'More explanation.']:
            with self.subTest(block=block):
                prefix='> How about now?\n\n'+r'\(\huge\text{⮑}\)'
                self.assertEqual([],reply.check(prefix+' The copy finished.\n\n'+block))
                self.assertTrue(reply.check(prefix+' '+reply.CARET+'\n\nThe copy finished.\n\n'+block))

    def test_nested_underlines_keep_colour_and_skill_link_validation(self):
        good=r'\(\color{#67e8f9}{\textsf{The viewer is a \underline{snapshot} of the file.}}\)'
        self.assertEqual([],reply.check(good))
        self.assertTrue(reply.check(good.replace('#67e8f9','gray')))
        self.assertTrue(reply.check(good.replace('textsf','textrm')))
        skill=r'\(\color{magenta}{\textrm{\underline{skill-creator}}}\)'
        self.assertTrue(reply.check(skill))
        self.assertEqual([],reply.check(skill+' [↗](/tmp/skill.html)',False))
