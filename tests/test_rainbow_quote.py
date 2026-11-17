import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import os
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import re

ROOT = Path(__file__).resolve().parents[1]

def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

quote = load('rainbow', 'rainbow-quote.py')
math = load('math_validation', 'math-validation.py')
checker = load('rainbow_reply_checker', 'check-reply.py')

# The fixed palette used before procedural blends; the ring formula must still
# reproduce it exactly so the colours keep the same brightness and saturation.
ORIGINAL_PALETTE = ('#fa7070', '#fa9370', '#fab570', '#fad870', '#fafa70', '#d8fa70', '#b5fa70', '#93fa70',
                    '#70fa70', '#70fa93', '#70fab5', '#70fad8', '#70fafa', '#70d8fa', '#70b5fa', '#7093fa',
                    '#7070fa', '#9370fa', '#b570fa', '#d870fa', '#fa70fa', '#fa70d8', '#fa70b5', '#fa7093')
SAMPLE_BLENDS = 20000

def colours_in(text):
    return re.findall(r'#[0-9a-f]{6}', text)

def channels(colour):
    return [int(colour[i:i + 2], 16) for i in (1, 3, 5)]

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, value):
        self.parts.append(value)

class RainbowRoute(unittest.TestCase):
    """The colour maths: vivid, steady, varied, exact and directly computable."""

    def test_ring_reproduces_original_palette_and_stays_vivid(self):
        self.assertEqual(list(ORIGINAL_PALETTE), [quote.ring_colour(quote.UNITS // 24 * i) for i in range(24)])
        ring = {quote.ring_colour(units) for units in range(quote.UNITS)}
        self.assertEqual(828, len(ring), 'Every possible colour: 6 sides x 138 channel values')
        for colour in ring:
            self.assertTrue(quote.is_rainbow_colour(colour), colour)
            self.assertEqual((112, 250), (min(channels(colour)), max(channels(colour))), colour)
        for status in ['#ef4444', '#22c55e', '#fb923c', '#67e8f9', '#b8a4d9', '#FA7070', 'magenta', '#fa707']:
            self.assertFalse(quote.is_rainbow_colour(status), status)

    def test_blends_are_steady_bounded_and_go_both_ways(self):
        jumps = [quote.blend_jump(blend) for blend in range(SAMPLE_BLENDS)]
        self.assertTrue(all(177 <= jump <= 317 or -237 <= jump <= -97 for jump in jumps),
                        'Smooth routes of about 42-138 degrees over six words')
        forward = sum(jump > 0 for jump in jumps) / len(jumps)
        self.assertGreater(forward, 0.45)
        self.assertLess(forward, 0.55)
        degrees_per_word = sum(map(abs, jumps)) / len(jumps) * 360 / quote.TICKS / quote.BLEND_WORDS
        self.assertAlmostEqual(15, degrees_per_word, delta=0.5, msg='Same average pace as the 24-colour cycle')
        self.assertEqual(quote.TICKS, len({quote.destination(blend) for blend in range(SAMPLE_BLENDS)}),
                         'Every hue step is used as a destination')
        for blend in range(300):
            start = quote.destination(blend)
            words = [quote.word_colour(blend * quote.BLEND_WORDS + offset) for offset in range(quote.BLEND_WORDS + 1)]
            self.assertEqual(quote.ring_colour(start * quote.BLEND_WORDS), words[0], 'Each blend starts on its destination')
            self.assertEqual(quote.ring_colour(quote.destination(blend + 1) * quote.BLEND_WORDS), words[-1],
                             'and reaches the next one after exactly six words')
            self.assertEqual(len(words), len(set(words)), 'Neighbouring words always differ')

    def test_revisited_colours_lead_to_different_destinations(self):
        green_start = quote.TICKS * 105 // 360
        green_end = quote.TICKS * 135 // 360
        green = range(green_start, green_end + 1)
        following = [quote.destination(blend + 1) for blend in range(SAMPLE_BLENDS) if quote.destination(blend) in green]
        self.assertGreater(len(following), 500)
        self.assertGreater(len(set(following)), 40, 'Green leads to many different next colours')
        warmer = [tick for tick in following if tick < green_start]  # towards yellow, orange and red
        cooler = [tick for tick in following if tick > green_end]    # towards cyan, blue and purple
        self.assertGreater(len(warmer), len(following) // 4)
        self.assertGreater(len(cooler), len(following) // 4)
        landings = []
        for blend in range(1, SAMPLE_BLENDS):
            if (quote.blend_jump(blend) > 0) != (quote.blend_jump(blend - 1) > 0):
                gap = (quote.destination(blend + 1) - quote.destination(blend - 1)) % quote.TICKS
                landings.append(min(gap, quote.TICKS - gap))
        self.assertTrue(all(10 <= gap <= 150 for gap in landings), 'Turning back lands about 4-66 degrees on')
        self.assertLess(sum(gap * 360 <= 30 * quote.TICKS for gap in landings) / len(landings), 0.5,
                        'Most turns reach new colour instead of bouncing within 30 degrees')
        jumps = [quote.blend_jump(blend) for blend in range(6000)]
        for period in range(1, 3000):
            self.assertNotEqual(jumps[:3000], jumps[period:period + 3000], f'Route shape repeats after {period} blends')

    def test_huge_positions_are_exact_deterministic_and_periodic(self):
        self.assertEqual(1242 * 2 ** 64, quote.PERIOD_WORDS)
        for position in [0, 5, 6 * quote.TICKS - 1, 10 ** 30, quote.PERIOD_WORDS - 1, 2 ** 200 + 7]:
            with self.subTest(position=position):
                colour = quote.word_colour(position)
                self.assertEqual(colour, quote.word_colour(position))
                self.assertEqual(colour, quote.word_colour(position + quote.PERIOD_WORDS))

                self.assertNotEqual(colour, quote.word_colour(position + 1), 'No float rounding merges neighbours')
        markup, _ = quote.render('Same question here', 'html', start_index=10 ** 30)
        self.assertEqual([quote.word_colour(10 ** 30 + i) for i in range(3)], colours_in(markup))
        for bad in [-1, 1.5, True, '3', None]:
            with self.assertRaises(ValueError):
                quote.word_colour(bad)

    def test_full_vivid_destination_range_and_short_quote_variety(self):
        destinations = {quote.ring_colour(quote.destination(i) * quote.BLEND_WORDS) for i in range(12000)}
        self.assertEqual(828, len(destinations), 'All native vivid shades can be destinations')
        profiles = {tuple(quote.word_colour(i * 12 + offset) for offset in range(12)) for i in range(10000)}
        self.assertGreaterEqual(len(profiles), 9990, 'Short references should rarely repeat an exact colour profile in this fixed sample')

    def test_reply_checker_recognises_generated_colours(self):
        markdown, _ = quote.render('Which way does the colour go next?', start_index=987654321)
        self.assertTrue(colours_in(markdown))
        self.assertTrue(all(checker.rainbow_quotes.is_rainbow_colour(colour) for colour in colours_in(markdown)))
        answer = r'\(\huge\text{⮑}\) \(\textsf{The colour heads somewhere new.}\)'
        without = markdown + '\n\n' + answer
        self.assertTrue(any('In response to' in error for error in checker.check(without)))
        with_context = '> **In response to:** How rainbow colours change.\n>\n' + markdown + '\n\n' + answer
        self.assertFalse(any('In response to' in error for error in checker.check(with_context)))


class RainbowQuotes(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.TemporaryDirectory()
        self.addCleanup(self.home.cleanup)
        patcher = patch.dict(os.environ, {'CODEX_HOME': self.home.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.state = Path(self.home.name)/'state/response-preferences/rainbow-next-word.txt'
        self.old_state = self.state.with_name('rainbow-next-index.txt')

    def run_cli(self, *args):
        return subprocess.run(['python3', str(ROOT/'scripts/rainbow-quote.py'), *map(str, args)],
                              text=True, capture_output=True, env={**os.environ, 'CODEX_HOME': self.home.name})

    def test_counter_reserves_word_runs_monotonically_and_serializes_callers(self):
        self.assertEqual([0, 3, 4], quote.reserve_word_positions([3, 1, 2]))
        self.assertEqual('6', self.state.read_text().strip())
        self.assertEqual(6, quote.next_start_index(5))
        with ThreadPoolExecutor(max_workers=8) as pool:
            values = list(pool.map(lambda _: quote.next_start_index(2), range(24)))
        self.assertEqual(list(range(11, 11 + 48, 2)), sorted(values))
        self.assertEqual(59, quote.next_start_index())
        for bad in [[], [0], [-1], [1.5], [True], [2, 0]]:
            with self.assertRaises(ValueError):
                quote.reserve_word_positions(bad)
        self.assertEqual('60', self.state.read_text().strip(), 'Rejected requests do not move the counter')

    def test_counter_never_wraps_and_leaves_old_palette_counter_alone(self):
        self.state.parent.mkdir(parents=True)
        # The old helper and Agent Flow keep writing this file as 0-23.
        self.old_state.write_text('23\n')
        self.assertEqual([0, 7], quote.reserve_word_positions([7, 4]))
        self.assertEqual('11', self.state.read_text().strip())
        self.old_state.write_text('3\n')
        self.assertEqual(11, quote.next_start_index(23))
        self.assertEqual('34', self.state.read_text().strip(), 'Old-counter writes never pull the route back')
        self.assertEqual('3\n', self.old_state.read_text())
        big = 10 ** 40
        self.state.write_text(str(big))
        self.assertEqual(big, quote.next_start_index(3))
        self.assertEqual(str(big + 3), self.state.read_text().strip())
        for broken in ['broken', '-3', '+3', '1_000', '1.5', '٣', '']:
            with self.subTest(broken=broken):
                self.state.write_text(broken)
                with self.assertRaises(ValueError):
                    quote.next_start_index()
                self.assertEqual(broken, self.state.read_text(), 'A broken counter is reported, not overwritten')

    def test_colour_rhythm_survives_wrapping_and_longer_quotes(self):
        words = ['word' + str(i) for i in range(51)]
        _, short = quote.render(' '.join(words[:7]), start_index=0)
        _, long = quote.render(' '.join(words), start_index=0)
        _, wrapped = quote.render('\n'.join(words), start_index=0)
        self.assertTrue(all(expression.startswith(r'\textsf{') for expression in long))
        self.assertIn(short[0].removeprefix(r'\textsf{').removesuffix('}'), long[0])
        self.assertEqual(long, wrapped)
        self.assertGreater(len(long), 1)
        self.assertEqual([quote.word_colour(i) for i in range(51)], colours_in(' '.join(long)))
        _, fallback = quote.render(' '.join(words[:23] + ['x' * 25, 'next']), start_index=0)
        self.assertIn(r'\color{' + quote.word_colour(24) + '}{next}', fallback[-1],
                      'A long word in code still uses its word position')

    def test_counter_chosen_once_per_quote_with_its_word_count(self):
        with patch.object(quote, 'next_start_index', return_value=10 ** 12) as rng:
            _, expressions = quote.render(' '.join(['word'] * 27))
            rng.assert_called_once_with(27)
        self.assertEqual([quote.word_colour(10 ** 12 + i) for i in range(27)], colours_in(' '.join(expressions)))
        with patch.object(quote, 'next_start_index') as rng:
            a = quote.render('Same question', start_index=23)
            b = quote.render('Same question', start_index=23)
            self.assertEqual(a, b)
            rng.assert_not_called()
        for bad in [-1, 1.5, True, '3']:
            with self.assertRaises(ValueError):
                quote.render('Question', start_index=bad)
        self.assertFalse(self.state.exists())

    def test_wording_survives_short_long_and_multilingual_quotes(self):
        samples = ['Why?', 'Can you make this easier to read?',
                   "What happens if we supply a type that's not compatible with the DTO class? Is it just a runtime error?",
                   'Why is C# at 54% with sample_tool, A & B, {name}, $5, ~x and C:\\work?',
                   'Does <script>alert(1)</script> stay literal?', 'Pourquoi déjà? 日本語の質問もあります。',
                   'These words need to stay in exactly the same order. ' * 30]
        for sample in samples:
            with self.subTest(sample=sample[:70]):
                self.assertEqual(' '.join(sample.split()), ' '.join(quote.chunks(sample)))
                markup, expressions = quote.render(sample, 'html')
                parsed = Text(); parsed.feed(markup)
                self.assertEqual(' '.join(sample.split()), ''.join(parsed.parts))
                self.assertNotIn('<script>', markup)
                self.assertEqual([None] * len(expressions), math.render_errors(expressions))
                self.assertTrue(all(quote.tex(chunk) not in " ".join(expressions) for chunk in quote.chunks(sample) if len(chunk) > 24))
                _, expressions = quote.render(sample, start_index=4321)
                self.assertTrue(all(checker.prose_length(e) <= checker.MAX_PROSE_CHARACTERS for e in expressions))
                self.assertEqual([None] * len(expressions), math.render_errors(expressions))

    def test_long_literal_is_not_an_unbreakable_math_box(self):
        value = 'Why ' + 'long_identifier_' * 10 + '`embedded`?'
        markdown, expressions = quote.render(value)
        self.assertIn('`` ', markdown)
        self.assertFalse(any('long' in expression for expression in expressions))
        self.assertEqual([None] * len(expressions), math.render_errors(expressions))

    def test_cli_checks_punctuation_and_refuses_empty_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'question.txt'
            path.write_text('Can C# accept 54% & sample_tool?')
            result = self.run_cli(path)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(result.stdout.startswith('> '))
            self.assertIn(r'C\#', result.stdout)
            self.assertIn(r'54\%', result.stdout)
            self.assertEqual('6', self.state.read_text().strip(), 'Six words reserve six positions')
            path.write_text('  \n')
            result = self.run_cli(path)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual('', result.stdout)
            self.assertEqual('6', self.state.read_text().strip())

    def test_cli_batches_multiple_quotes_with_one_reservation(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / 'first.txt'
            second = Path(directory) / 'second.txt'
            first.write_text('First question?')
            second.write_text('Second question here?')
            result = self.run_cli(first, second)
            self.assertEqual(0, result.returncode, result.stderr)
            blocks = result.stdout.strip().split('\n\n')
            self.assertEqual(2, len(blocks))
            self.assertEqual([quote.word_colour(i) for i in range(2)], colours_in(blocks[0]))
            self.assertEqual([quote.word_colour(i) for i in range(2, 5)], colours_in(blocks[1]),
                             'The second quote continues where the first ended')
            self.assertEqual('5', self.state.read_text().strip())

            pinned = 123456789012345678901234567890
            result = self.run_cli('--start-index', pinned, first, second)
            self.assertEqual(0, result.returncode, result.stderr)
            blocks = result.stdout.strip().split('\n\n')
            self.assertEqual([quote.word_colour(pinned + i) for i in range(2)], colours_in(blocks[0]))
            self.assertEqual([quote.word_colour(pinned + i) for i in range(2, 5)], colours_in(blocks[1]))
            self.assertEqual('5', self.state.read_text().strip(), 'A pinned start never moves the counter')

    def test_cli_rejects_bad_start_indexes_before_touching_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'question.txt'
            path.write_text('Which colour comes next?')
            for bad in ['-1', '+1', '1_000', '1.0', '1e3', ' 7', '٣', '']:
                with self.subTest(bad=bad):
                    result = self.run_cli('--start-index', bad, path)
                    self.assertNotEqual(0, result.returncode)
                    self.assertEqual('', result.stdout)
                    self.assertIn('--start-index', result.stderr)
                    self.assertFalse(self.state.exists())

    def test_cli_accepts_eighty_characters_and_rejects_eighty_one(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'question.txt'
            for length, expected_returncode in [(80, 0), (81, 1)]:
                path.write_text('Why ' * 19 + 'now?' + '?' * (length - 80))
                result = self.run_cli(path)
                self.assertEqual(expected_returncode, result.returncode, result.stderr)
                self.assertEqual('20', self.state.read_text().strip(), 'Rejected quote must not advance the colours')
                if expected_returncode:
                    self.assertEqual('', result.stdout)
                    self.assertIn('80 characters or fewer', result.stderr)

    def test_cli_rejects_long_reminder_before_reserving_batch(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / 'first.txt'
            second = Path(directory) / 'second.txt'
            first.write_text('Can you check this?')
            second.write_text('Could this entire long question be repeated across more than one line, while keeping all its extra details in the rainbow reminder?')
            result = self.run_cli(first, second)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual('', result.stdout)
            self.assertIn('80 characters or fewer', result.stderr)
            self.assertFalse(self.state.exists(), 'Invalid batch must not advance the colours')
            second.write_text('Can this question wrap while keeping the useful detail about what I was asking?')
            result = self.run_cli(first, second)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual('18', self.state.read_text().strip())

    def test_long_demo_needs_a_pinned_start_and_keeps_normal_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'story.txt'
            words = ['colour{}'.format(i) for i in range(150)]
            path.write_text(' '.join(words))
            result = self.run_cli(path)
            self.assertNotEqual(0, result.returncode, 'Normal reminders still reject long text')
            result = self.run_cli('--long-demo', path)
            self.assertNotEqual(0, result.returncode)
            self.assertIn('--start-index', result.stderr)
            result = self.run_cli('--long-demo', '--start-index', 600, path)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual([quote.word_colour(600 + i) for i in range(150)], colours_in(result.stdout))
            expressions = re.findall(r'\\\((.*?)\\\)', result.stdout)
            self.assertGreater(len(expressions), 10)
            self.assertTrue(all(len(re.sub(r'\\color\{[^}]*\}|\\textsf\{|[{}]', '', e)) <= 64 for e in expressions))
            self.assertEqual([None] * len(expressions), math.render_errors(expressions))
            result = self.run_cli('--long-demo', '--claude', '--start-index', 600, path)
            self.assertNotEqual(0, result.returncode, 'Claude keeps its 8-word reminder rule')
            self.assertEqual('', result.stdout)
            self.assertFalse(self.state.exists(), 'Demos never touch the counter')

    def test_cli_claude_mode_keeps_reminders_renderable_in_claude(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'question.txt'
            def run(text):
                path.write_text(text)
                return self.run_cli('--claude', path)
            result = run('Did we discuss running worktree code in the cloud?')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('8 words or fewer', result.stderr)
            self.assertFalse(self.state.exists(), 'A rejected word count must not advance the colours')
            result = run('Is $8 from unusually heavy testing?')
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn(r'{\textdollar{}8}', result.stdout)
            self.assertNotIn('$', result.stdout)
            result = run('Should parallel worktree deployments share one staging project?')
            self.assertNotEqual(0, result.returncode)
            self.assertIn('208-character', result.stderr)
            self.assertEqual('', result.stdout)

if __name__ == '__main__':
    unittest.main()
