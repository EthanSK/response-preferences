import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('math_validation', Path(__file__).resolve().parents[1] / 'scripts/math-validation.py')
math = importlib.util.module_from_spec(spec)
spec.loader.exec_module(math)


class RendererChecks(unittest.TestCase):
    def test_literal_text_and_real_math(self):
        bad = [r'\underline{\textsf{C# task}}', r'\textsf{A & B}', r'\textsf{sample_tool}', r'\textsf{54%}', r'\underline{\textsf{missing brace}', r'\unknowncommand{x}', r'\textsf{Value \ensuremath{x_i}}']
        self.assertTrue(all(math.render_errors(bad)))
        good = [r'\textsf{C\# task}', r'\textsf{A \& B}', r'\textsf{sample\_tool}', r'\textsf{54\%}', r'\textsf{a\{b\}}', r'x_i^2', r'\frac{1}{2}', r'\color{#67e8f9}{\textsf{A fact.}}', r'\huge\text{🧪}', r'\raisebox{0.3em}{\Large\text{⌄}}']
        self.assertEqual([None] * len(good), math.render_errors(good))

    def test_untrusted_and_runaway_commands_do_not_pass(self):
        self.assertTrue(all(math.render_errors([r'\href{https://example.com}{x}', r'\includegraphics{https://example.com/a.png}', r'\def\x{\x}\x'])))

    def test_delimiters_and_multiline(self):
        for text in [r'\(x', r'x\)', r'\(x\]', '$$x', r'\(x\(y\)']:
            self.assertTrue(math.check_math(text), text)
        self.assertEqual([], math.check_math('\\[\nx_i\n\\]'))
        self.assertEqual([], math.check_math('$$x_i$$'))
        self.assertTrue(math.check_math('\\(\\textsf{C#\n task}\\)'))

    def test_quoted_and_code_evidence_is_not_authored_math(self):
        text = '> \\(\\textsf{C#}\\)\n\n`\\(broken`\n\n```tex\n\\(broken\n```\n\nOrdinary C#, 54%, sample_tool and $5.'
        self.assertEqual([], math.check_math(text))
        self.assertEqual([], math.check_math(r'\\(literal escaped delimiters\\)'))

    def test_missing_runtime_and_bad_helper_fail_closed(self):
        with patch.dict(math.os.environ, {}, clear=True), patch.object(math.shutil, 'which', return_value=None):
            self.assertIn('unavailable', math.check_math(r'\(x\)')[0])
        for error in [OSError(), subprocess.TimeoutExpired('node', 8)]:
            with patch.object(math.subprocess, 'run', side_effect=error):
                self.assertIn('unavailable', math.check_math(r'\(x\)')[0])
        with patch.object(math.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '{}')):
            self.assertIn('unavailable', math.check_math(r'\(x\)')[0])

    def test_batch_rejects_oversized_expression(self):
        self.assertTrue(math.render_errors(['x' * 10001])[0])
