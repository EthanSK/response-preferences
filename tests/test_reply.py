import importlib.util
from pathlib import Path
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('reply',Path(__file__).resolve().parents[1]/'scripts/check-reply.py')
reply=importlib.util.module_from_spec(spec);spec.loader.exec_module(reply)
TOPIC = r'\(\color{#b8a4d9}{\textsf{About: the requested file change and its current status.}}\)'
def check_message(text, **kwargs):
    return reply.check(text+'\n\n'+TOPIC, **kwargs)

def check_fragment(*args, **kwargs):
    return reply.check(*args, require_pointer=False, require_topic=False, **kwargs)

class ReplyChecks(unittest.TestCase):
    def test_historical_plain_skill_announcement_is_rejected(self):
        self.assertTrue(check_fragment(r'\(\huge\text{🧠}\) Skill use: browser-test-on-macbook and use-macbook-display — open the site.'))
    def test_each_coloured_skill_requires_its_own_existing_link(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'skill.html';p.write_text('example')
            good=rf'\(\huge\text{{🧠}}\) **Skill use:** \(\color{{magenta}}{{\textrm{{skill-creator}}}}\) [↗]({p}) — update the skill.'
            self.assertEqual([],check_fragment(good))
            self.assertTrue(check_fragment(good.replace(f'[↗]({p})','')))
            p.unlink();self.assertTrue(check_fragment(good))
    def test_regressed_marker_and_colour_patterns_are_rejected(self):
        for draft in [r'\(\Huge\text{✅}\) Done.',r'Done. \(\huge\text{✅}\)',r'\(\huge\text{🎯}\) Explanation.',r'\(\huge\text{➕}\) Added.',r'\(\color{gray}{\textsf{A fact}}\)',r'\(\color{magenta}{\textsf{skill-creator}}\)']:
            with self.subTest(draft=draft):self.assertTrue(check_fragment(draft))
    def test_quotes_and_code_examples_do_not_become_new_instructions(self):
        self.assertEqual([],check_fragment('> Earlier response: '+r'\(\Huge\text{🎯}\)'+'\n\n```md\n<!-- example -->\n```'))
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
        self.assertTrue(check_message(r'\(\huge\text{✅}\) Saved.'))
        self.assertEqual([], check_message(r'\(\huge\text{👉}\) The change is saved.'))
        self.assertEqual([], check_message(r'\(\huge\text{🫵}\) Choose the destination.'))
        self.assertEqual([], check_message(r'\(\huge\text{✅}\) \(\huge\text{👉}\) The change is saved.'))
        self.assertTrue(check_message('> 🫵 Your earlier action.\n\n```text\n👉 example\n```\n\nSaved.'))
        self.assertTrue(check_message(r'\(\huge\text{👉}\) '+reply.CARET+'\n\nThe result.'))

    def test_commentary_reserves_fingers_for_final(self):
        self.assertEqual([], check_message('🐌 Checking the files.', require_pointer=False, commentary=True))
        for finger in ['👉', '🫵']:
            self.assertTrue(check_message('\\(\\huge\\text{'+finger+'}\\) Read this.', require_pointer=False, commentary=True))
            self.assertTrue(check_message(finger+' Read this.', require_pointer=False, commentary=True))

    def test_marker_sizes_depend_on_reply_phase(self):
        for symbol in reply.MARKERS - {'🫵', '👉'}:
            with self.subTest(symbol=symbol):
                prefix = '> Check the files.\n\n' if symbol == '⮑' else ''
                plain = prefix + symbol + ' Checking the files.'
                large = prefix + r'\(\huge\text{' + symbol + r'}\) Checking the files.'
                self.assertEqual([], check_fragment(plain, commentary=True))
                self.assertTrue(check_fragment(large, commentary=True))
                self.assertEqual([], check_fragment(large))
                self.assertTrue(check_fragment(plain))
        for wrapper in [r'\(\Large\text{ⓘ}\)', r'\(\Huge\text{ⓘ}\)', r'\(\text{ⓘ}\)']:
            self.assertTrue(check_fragment(wrapper+' Details.', commentary=True))

    def test_small_commentary_markers_keep_structure_and_reference_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'skill.html'; p.write_text('example')
            good=rf'🧠 **Skill use:** \(\color{{magenta}}{{\textrm{{skill-creator}}}}\) [↗]({p}) — check the files.'
            self.assertEqual([],check_fragment(good,commentary=True))
            self.assertEqual([],check_fragment(good.replace('🧠 ', '🧠 ⌄\n\n'),commentary=True))
            self.assertTrue(check_fragment(good.replace('🧠','🎯'),commentary=True))
            self.assertTrue(check_fragment(good.replace(f'[↗]({p})',''),commentary=True))
            self.assertTrue(check_fragment('🧠 Skill use: skill-creator.',commentary=True))
            p.unlink(); self.assertTrue(check_fragment(good,commentary=True))
        self.assertEqual([],check_fragment('ⓘ ⌄\n\nFirst fact.\n\nSecond fact.',commentary=True))
        for bad in ['ⓘ', 'ⓘ '+reply.CARET, 'ⓘ ⌄ Details.', '🎯 Details.', '⮑ Answer.', '> Question?\n\n⮑ ⌄\n\nAnswer.', '  ⓘ Indented.']:
            self.assertTrue(check_fragment(bad,commentary=True),bad)
        self.assertEqual([],check_fragment('> Earlier: '+r'\(\huge\text{🧠}\)'+'\n\n```text\n👉 example\n```\n\nⓘ Details.\n\n| Item | Status |\n|---|---|\n| Check | ✅ Passed |',commentary=True))


    def test_topic_reminder_is_required_in_final_and_commentary(self):
        for body, options in [(r'\(\huge\text{👉}\) The file is saved.', {}),
                              ('🐌 Saving the file.', {'commentary': True, 'require_pointer': False})]:
            with self.subTest(options=options):
                self.assertTrue(reply.check(body, **options))
                self.assertEqual([], reply.check(body+'\n\n'+TOPIC+'\n', **options))

    def test_topic_reminder_must_follow_actions_quotes_and_code(self):
        body=r'\(\huge\text{🫵}\) Choose the destination.'
        for later in [body, '> Additional quoted context', '```text\nLater example\n```']:
            self.assertTrue(reply.check(body+'\n\n'+TOPIC+'\n\n'+later))
        self.assertTrue(reply.check(body+'\n\n'+TOPIC+'\n\n'+TOPIC))
        self.assertTrue(reply.check(body+'\n\n> '+TOPIC))
        self.assertTrue(reply.check(body+'\n\n```text\n'+TOPIC+'\n```'))

    def test_lavender_is_reserved_for_nonempty_topic_labels(self):
        for invalid in [TOPIC.replace('About: ', ''), TOPIC.replace('textsf', 'textrm'),
                        'More text '+TOPIC, r'\(\color{#b8a4d9}{\textsf{About: }}\)']:
            self.assertTrue(reply.check(r'\(\huge\text{👉}\) Saved.'+'\n\n'+invalid))


    def test_topic_reminder_can_wrap_between_short_lavender_expressions(self):
        overview = r'\(\color{#b8a4d9}{\textsf{About: fixing the video export.}}\)'
        detail = r'\(\color{#b8a4d9}{\textsf{Restart the app, then retry the clip.}}\)'
        for body, options in [(r'\(\huge\text{👉}\) Restart to use the export fix.', {}),
                              ('🐌 Checking the export fix.', {'commentary': True, 'require_pointer': False})]:
            self.assertEqual([], reply.check(body+'\n\n'+overview+' '+detail, **options))
            for bad in [overview+' '+overview, overview+' stray text '+detail,
                        overview+' '+detail.replace('#b8a4d9', '#67e8f9'),
                        overview+' '+detail.replace('textsf', 'textrm'),
                        overview+' '+detail.replace('Restart the app, then retry the clip.', '')]:
                self.assertTrue(reply.check(body+'\n\n'+bad, **options), bad)

    def test_oversized_inline_prose_is_rejected_without_hiding_nested_underlines(self):
        long_warning = r'\(\color{#fb923c}{\textsf{The \underline{release is still pending}: its working copy has \underline{many outstanding changes}, needs \underline{another review before publication}, and its last recorded task run was interrupted.}}\)'
        self.assertTrue(any('may overflow' in e for e in check_fragment(long_warning)))
        short = r'\(\color{#fb923c}{\textsf{The \underline{release is still pending}.}}\) The dependency needs another review before publication.'
        self.assertEqual([], check_fragment(short))
        self.assertEqual([], check_fragment(short, commentary=True))
        for prefix in [r'\underline{\textsf{', r'\color{#67e8f9}{\textsf{', r'\color{#b8a4d9}{\textsf{About: ']:
            self.assertTrue(any('may overflow' in e for e in check_fragment(r'\('+prefix+'A long but meaningful statement. '*5+r'}}\)')))
        self.assertEqual([], check_fragment('> '+long_warning+'\n\n```md\n'+long_warning+'\n```\n\n`'+long_warning+'`'))
        self.assertEqual([], check_fragment(r'\('+'x + '*100+r'y\)'))

    def test_prose_length_counts_visible_words_not_wrapper_names(self):
        self.assertEqual(len('The release is still pending.'), reply.prose_length(r'\color{#fb923c}{\textsf{The \underline{release is still pending}.}}'))
        self.assertEqual(5, reply.prose_length(r'\textsf{A \& B}'))
        self.assertEqual([], check_fragment(r'\(\textsf{'+'x'*80+r'}\)'))
        self.assertTrue(any('may overflow' in e for e in check_fragment(r'\(\textsf{'+'x'*81+r'}\)')))
