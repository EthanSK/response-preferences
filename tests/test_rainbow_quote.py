import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import os
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]

def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

quote = load('rainbow', 'rainbow-quote.py')
math = load('math_validation', 'math-validation.py')

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, value):
        self.parts.append(value)

class RainbowQuotes(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.TemporaryDirectory()
        self.addCleanup(self.home.cleanup)
        patcher = patch.dict(os.environ, {'CODEX_HOME': self.home.name})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_counter_persists_wraps_and_serializes_concurrent_callers(self):
        self.assertEqual(list(range(24)) + [0, 1], [quote.next_start_index() for _ in range(26)])
        with ThreadPoolExecutor(max_workers=8) as pool:
            values = list(pool.map(lambda _: quote.next_start_index(), range(24)))
        self.assertEqual(list(range(24)), sorted(values))
        self.assertEqual(2, quote.next_start_index())
        state = Path(self.home.name)/'state/response-preferences/rainbow-next-index.txt'
        state.write_text('broken')
        with self.assertRaises(ValueError):
            quote.next_start_index()

    def test_batch_reserves_consecutive_offsets_with_one_counter_update(self):
        self.assertEqual([0, 1, 2], quote.reserve_start_indices(3))
        self.assertEqual(3, quote.next_start_index())
        self.assertEqual(list(range(4, 24)) + [0, 1], quote.reserve_start_indices(22))
        self.assertEqual(2, quote.next_start_index())
        for bad in [0, -1, 1.5]:
            with self.assertRaises(ValueError):
                quote.reserve_start_indices(bad)

    def test_colour_rhythm_survives_wrapping_and_longer_quotes(self):
        words = ['word' + str(i) for i in range(51)]
        _, short = quote.render(' '.join(words[:7]), start_index=0)
        _, long = quote.render(' '.join(words), start_index=0)
        _, wrapped = quote.render('\n'.join(words), start_index=0)
        self.assertIn(short[0].removeprefix(r'\textsf{').removesuffix('}'), long[0])
        self.assertEqual(long, wrapped)
        self.assertGreater(len(long), 1)
        joined = ' '.join(long)
        self.assertIn(r'\color{#fa7093}{word23}', joined)
        self.assertIn(r'\color{#fa7070}{word24}', joined)
        self.assertIn(r'\color{#fa9370}{word25}', joined)
        _, fallback = quote.render(' '.join(words[:23] + ['x' * 25, 'next']), start_index=0)
        self.assertIn(r'\color{#fa7070}{next}', fallback[-1])

    def test_counter_chosen_once_per_quote_and_all_offsets_wrap(self):
        for start in range(24):
            with patch.object(quote, 'next_start_index', return_value=start) as rng:
                _, expressions = quote.render(' '.join(['word'] * 27))
                rng.assert_called_once_with()
            self.assertGreater(len(expressions), 1)
            joined = ' '.join(expressions)
            for i in range(27):
                self.assertIn(quote.PALETTE[(start + i) % 24], joined)
        with patch.object(quote, 'next_start_index') as rng:
            a = quote.render('Same question', start_index=23)
            b = quote.render('Same question', start_index=23)
            self.assertEqual(a, b)
            rng.assert_not_called()
        for bad in [-1, 24]:
            with self.assertRaises(ValueError):
                quote.render('Question', start_index=bad)

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
            result = subprocess.run(['python3', str(ROOT/'scripts/rainbow-quote.py'), str(path)], text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(result.stdout.startswith('> '))
            self.assertIn(r'C\#', result.stdout)
            self.assertIn(r'54\%', result.stdout)
            path.write_text('  \n')
            result = subprocess.run(['python3', str(ROOT/'scripts/rainbow-quote.py'), str(path)], text=True, capture_output=True)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual('', result.stdout)

    def test_cli_batches_multiple_quotes_with_one_reservation(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / 'first.txt'
            second = Path(directory) / 'second.txt'
            first.write_text('First question?')
            second.write_text('Second question?')
            result = subprocess.run(
                ['python3', str(ROOT/'scripts/rainbow-quote.py'), str(first), str(second)],
                text=True, capture_output=True, env={**os.environ, 'CODEX_HOME': self.home.name})
            self.assertEqual(0, result.returncode, result.stderr)
            blocks = result.stdout.strip().split('\n\n')
            self.assertEqual(2, len(blocks))
            self.assertIn(quote.PALETTE[0], blocks[0])
            self.assertIn(quote.PALETTE[1], blocks[1])
            state = Path(self.home.name)/'state/response-preferences/rainbow-next-index.txt'
            self.assertEqual('2', state.read_text().strip())

            result = subprocess.run(
                ['python3', str(ROOT/'scripts/rainbow-quote.py'), '--start-index', '23', str(first), str(second)],
                text=True, capture_output=True, env={**os.environ, 'CODEX_HOME': self.home.name})
            self.assertEqual(0, result.returncode, result.stderr)
            blocks = result.stdout.strip().split('\n\n')
            self.assertIn(quote.PALETTE[23], blocks[0])
            self.assertIn(quote.PALETTE[0], blocks[1])
            self.assertEqual('2', state.read_text().strip())

if __name__ == '__main__':
    unittest.main()
