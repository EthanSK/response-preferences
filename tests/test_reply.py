import importlib.util
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('reply',Path(__file__).resolve().parents[1]/'scripts/check-reply.py')
reply=importlib.util.module_from_spec(spec);spec.loader.exec_module(reply)
def check_fragment(*args, **kwargs):
    return reply.check(*args, require_pointer=False, **kwargs)

class ReplyChecks(unittest.TestCase):
    def test_historical_plain_skill_announcement_is_rejected(self):
        self.assertTrue(check_fragment(r'\(\huge\text{🎯}\) Skill use: browser-test-on-macbook and use-macbook-display — open the site.'))
    def test_each_coloured_skill_requires_its_own_existing_link(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'skill.html';p.write_text('example')
            good=rf'\(\huge\text{{🎯}}\) **Skill use:** \(\color{{magenta}}{{\textrm{{skill-creator}}}}\) [↗]({p}) — update the skill.'
            self.assertEqual([],check_fragment(good))
            self.assertTrue(check_fragment(good.replace(f'[↗]({p})','')))
            p.unlink();self.assertTrue(check_fragment(good))
    def test_regressed_marker_and_colour_patterns_are_rejected(self):
        for draft in [r'\(\Huge\text{✅}\) Done.',r'Done. \(\huge\text{✅}\)',r'\(\huge\text{🧠}\) Explanation.',r'\(\huge\text{➕}\) Added.',r'\(\color{gray}{\textsf{A fact}}\)',r'\(\color{magenta}{\textsf{skill-creator}}\)']:
            with self.subTest(draft=draft):self.assertTrue(check_fragment(draft))
    def test_quotes_and_code_examples_do_not_become_new_instructions(self):
        self.assertEqual([],check_fragment('> Earlier response: '+r'\(\Huge\text{🧠}\)'+'\n\n```md\n<!-- example -->\n```'))
    def test_direct_answer_needs_its_question_quote(self):
        answer=r'\(\huge\text{⮑}\) The quote line is restored.'
        self.assertTrue(check_fragment(answer))
        self.assertEqual([],check_fragment('> Bring back the quotes.\n\n'+answer))
    def test_colour_cannot_be_a_link_label(self):
        self.assertTrue(check_fragment(r'[\(\color{#22c55e}{\textsf{Saved}}\)](/tmp/file.html)',False))
    def test_inline_information_and_multi_block_sections_are_valid(self):
        self.assertEqual([],check_fragment(r'\(\huge\text{✅}\) '+r'\(\color{#22c55e}{\textsf{Saved.}}\)'+'\n\n'+r'\(\huge\text{ⓘ}\) '+reply.CARET+'\n\nFirst fact.\n\nSecond fact.'))
    def test_silent_preference_use_needs_no_announcement(self):
        self.assertEqual([],check_fragment(r'\(\huge\text{ⓘ}\) This is an explanation.'))
    def test_metadata_and_old_markdown_links_are_rejected(self):
        for draft in ['<!-- codex-notification {} -->','[↗](/tmp/SKILL.md)','[open](/tmp/skill.html)']:
            self.assertTrue(check_fragment(draft,False))

    def test_standalone_caret_does_not_leak_to_inline_markers(self):
        self.assertTrue(check_fragment(r'\(\huge\text{ⓘ}\)'+'\n\nDetails below.'))
        self.assertEqual([],check_fragment(r'\(\huge\text{ⓘ}\) '+reply.CARET+'\n\nDetails below.'))
        self.assertTrue(check_fragment(r'\(\huge\text{✅}\) ▾ Saved.'))
        self.assertTrue(check_fragment(r'\(\huge\text{✅}\) '+reply.CARET+' Saved.'))
        self.assertEqual([],check_fragment(r'\(\huge\text{✅}\) Saved.'))

    def test_answer_stays_inline_before_supporting_blocks(self):
        for block in ['| Item | Status |\n|---|---|\n| Copy | Done |', '- First item\n- Second item', '```text\nexample\n```', 'More explanation.']:
            with self.subTest(block=block):
                prefix='> How about now?\n\n'+r'\(\huge\text{⮑}\)'
                self.assertEqual([],check_fragment(prefix+' The copy finished.\n\n'+block))
                self.assertTrue(check_fragment(prefix+' '+reply.CARET+'\n\nThe copy finished.\n\n'+block))

    def test_nested_underlines_keep_colour_and_skill_link_validation(self):
        good=r'\(\color{#67e8f9}{\textsf{The viewer is a \underline{snapshot} of the file.}}\)'
        self.assertEqual([],check_fragment(good))
        self.assertTrue(check_fragment(good.replace('#67e8f9','gray')))
        self.assertTrue(check_fragment(good.replace('textsf','textrm')))
        skill=r'\(\color{magenta}{\textrm{\underline{skill-creator}}}\)'
        self.assertTrue(check_fragment(skill))
        self.assertEqual([],check_fragment(skill+' [↗](/tmp/skill.html)',False))

    def test_old_tiny_section_caret_is_rejected(self):
        for caret in ['▾', '∨', '⌄', r'\(\LARGE\text{⌄}\)', r'\(\Large\text{⌄}\)']:
            self.assertTrue(check_fragment(r'\(\huge\text{ⓘ}\) '+caret+'\n\nSection details.'))
        self.assertEqual([],check_fragment(r'\(\huge\text{ⓘ}\) '+reply.CARET+'\n\nSection details.'))

    def test_computer_marker_is_global_and_project_extensions_are_scoped(self):
        self.assertEqual([],check_fragment(r'\(\huge\text{🖥️}\) Manual browser test passed.'))
        example=r'\(\huge\text{🧪}\) Project-specific fixture.'
        self.assertTrue(check_fragment(example))
        self.assertEqual([],check_fragment(example, approved_project_markers=['🧪']))
        self.assertTrue(check_fragment(example))

    def test_every_reply_needs_an_attention_finger(self):
        self.assertTrue(reply.check(r'\(\huge\text{✅}\) Saved.'))
        self.assertEqual([], reply.check(r'\(\huge\text{👉}\) The change is saved.'))
        self.assertEqual([], reply.check(r'\(\huge\text{🫵}\) Choose the destination.'))
        self.assertEqual([], reply.check(r'\(\huge\text{✅}\) \(\huge\text{👉}\) The change is saved.'))
        self.assertTrue(reply.check('> 🫵 Your earlier action.\n\n```text\n👉 example\n```\n\nSaved.'))
        self.assertTrue(reply.check(r'\(\huge\text{👉}\) '+reply.CARET+'\n\nThe result.'))

    def test_commentary_reserves_fingers_for_final(self):
        self.assertEqual([], reply.check(r'\(\huge\text{🐌}\) Checking the files.', require_pointer=False, commentary=True))
        for finger in ['👉', '🫵']:
            self.assertTrue(reply.check('\\(\\huge\\text{'+finger+'}\\) Read this.', require_pointer=False, commentary=True))
