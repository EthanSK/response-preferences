import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
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
    def test_colour_rhythm_survives_wrapping_and_longer_quotes(self):
        words = ['word' + str(i) for i in range(51)]
        _, short = quote.render(' '.join(words[:7]))
        _, long = quote.render(' '.join(words))
        _, wrapped = quote.render('\n'.join(words))
        self.assertEqual(short, long[:7])
        self.assertEqual(long, wrapped)
        self.assertEqual(len(words), len(long))
        self.assertIn(r'\color{#fa7093}{\textsf{word23}}', long[23])
        self.assertIn(r'\color{#fa7070}{\textsf{word24}}', long[24])
        self.assertIn(r'\color{#fa9370}{\textsf{word25}}', long[25])
        _, fallback = quote.render(' '.join(words[:23] + ['x' * 25, 'next']))
        self.assertIn(r'\color{#fa7070}{\textsf{next}}', fallback[-1])

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

if __name__ == '__main__':
    unittest.main()
