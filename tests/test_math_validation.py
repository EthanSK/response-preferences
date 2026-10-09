import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('math_validation', Path(__file__).resolve().parents[1] / 'scripts/math-validation.py')
math = importlib.util.module_from_spec(spec)
spec.loader.exec_module(math)


class RendererChecks(unittest.TestCase):
    def visible_text(self, values):
        """Read rendered text nodes, excluding TeX source and underline glyphs."""
        node = os.environ.get('RESPONSE_PREFERENCES_NODE') or shutil.which('node')
        script = r'''
const katex = require('katex');
let input = '';
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => process.stdout.write(JSON.stringify(
  JSON.parse(input).map(value => katex.renderToString(value, {
    output: 'mathml', throwOnError: true, strict: 'error', trust: false
  }))
)));
'''
        result = subprocess.run(
            [node, '-e', script], input=json.dumps(values), text=True,
            capture_output=True, cwd=Path(__file__).resolve().parents[1],
            timeout=8, check=True,
        )
        return [
            ''.join(''.join(n.itertext()) for n in ET.fromstring(html).iter()
                    if n.tag == '{http://www.w3.org/1998/Math/MathML}mtext')
            .replace('\u00a0', ' ')
            for html in json.loads(result.stdout)
        ]

    def test_literal_text_and_real_math(self):
        bad = [r'\underline{\textsf{C# task}}', r'\textsf{A & B}', r'\textsf{sample_tool}', r'\textsf{54%}', r'\underline{\textsf{missing brace}', r'\unknowncommand{x}', r'\textsf{Value \ensuremath{x_i}}']
        self.assertTrue(all(math.render_errors(bad)))
        good = [r'\textsf{C\# task}', r'\textsf{A \& B}', r'\textsf{sample\_tool}', r'\textsf{54\%}', r'\textsf{a\{b\}}', r'x_i^2', r'\frac{1}{2}', r'\color{#67e8f9}{\textsf{A fact.}}', r'\huge\text{🧪}', r'\raisebox{0.3em}{\Large\text{⌄}}']
        self.assertEqual([None] * len(good), math.render_errors(good))

    def test_untrusted_and_runaway_commands_do_not_pass(self):
        self.assertTrue(all(math.render_errors([r'\href{https://example.com}{x}', r'\includegraphics{https://example.com/a.png}', r'\def\x{\x}\x'])))

    def test_prices_render_with_currency_in_plain_and_styled_text(self):
        broken = r'\(\underline{\textsf{Pro $500 upgrade grants access}}\)'
        self.assertTrue(any('KaTeX parse error' in error for error in math.check_math(broken)))
        valid_prices = [
            'The price is $500/month.',
            r'\(\underline{\textsf{Pro \$500 upgrade grants access}}\)',
            r'\(\textsf{\color{#67e8f9}The price is \$99.95.}\)',
            r'\(\textsf{\color{#b8a4d9}About: A \$20,000 budget.}\)',
            r'The \(\underline{\textsf{Pro upgrade grants access}}\), at $500/month.',
        ]
        for price in valid_prices:
            with self.subTest(price=price):
                self.assertEqual([], math.check_math(price))

    def test_percent_cues_preserve_the_complete_visible_text(self):
        cues = ['10% cheaper than Balanced',
                'about 20% lower compute-plus-transfer cost']
        corrected = []
        for cue in cues:
            with self.subTest(cue=cue):
                broken = r'\(\underline{\textsf{' + cue + r'}}\)'
                self.assertTrue(any('KaTeX parse error' in e
                                    for e in math.check_math(broken)))
                fixed = broken.replace('%', r'\%')
                self.assertEqual([], math.check_math(fixed))
                corrected.append(r'\underline{\textsf{' + cue.replace('%', r'\%') + '}}')
        self.assertEqual(cues, self.visible_text(corrected))

    def test_styled_literal_symbols_preserve_visible_text(self):
        samples = [
            ('10%', r'10\%'), ('$99.95', r'\$99.95'),
            ('C#', r'C\#'), ('sample_tool', r'sample\_tool'),
            ('A & B', r'A \& B'), ('{name}', r'\{name\}'),
            ('~', r'\textasciitilde{}'), ('^', r'\textasciicircum{}'),
            ('\\', r'\textbackslash{}'),
            ('The price is $99.95, down 10%.',
             r'The price is \$99.95, down 10\%.'),
        ]
        expected, rendered = [], []
        wrappers = [r'\underline{\textsf{CONTENT}}',
                    r'\textsf{\color{#67e8f9}CONTENT}',
                    r'\textsf{\color{#b8a4d9}About: CONTENT}']
        for wrapper in wrappers:
            for literal, escaped in samples:
                expression = wrapper.replace('CONTENT', escaped)
                rendered.append(expression)
                expected.append(('About: ' if 'About:' in wrapper else '') + literal)
        self.assertEqual([], math.check_math('\n'.join(r'\(' + value + r'\)' for value in rendered)))
        self.assertEqual(expected, self.visible_text(rendered))
        self.assertEqual([], math.check_math('Plain 10%, $500, C#, sample_tool, A & B, {name}, ~, ^ and \\.'))

    def test_delimiters_and_multiline(self):
        for text in [r'\(x', r'x\)', r'\(x\]', '$$x', r'\(x\(y\)']:
            self.assertTrue(math.check_math(text), text)
        self.assertEqual([], math.check_math('\\[\nx_i\n\\]'))
        self.assertEqual([], math.check_math('$$x_i$$'))
        self.assertTrue(math.check_math('\\(\\textsf{C#\n task}\\)'))

    def test_response_formatting_requires_intact_explicit_delimiters(self):
        broken_close = r'But \(\underline{\textsf{different shapes still have current callers}}\\):'
        bare = r'But \underline{\textsf{different shapes still have current callers}}:'
        correct = r'But \(\underline{\textsf{different shapes still have current callers}}\):'
        self.assertIn('opening delimiter has no closing delimiter', ' '.join(math.check_math(broken_close)))
        self.assertIn('outside explicit math delimiters', ' '.join(math.check_math(bare)))
        self.assertEqual([], math.check_math(correct))

    def test_closed_formatting_braces_do_not_close_math_expression(self):
        broken = r'The video is \(\underline{\textsf{made fixed-size once}}, so rendering stays simple.'
        correct = broken.replace(r'once}},', r'once}}\),')
        self.assertIn('opening delimiter has no closing delimiter', ' '.join(math.check_math(broken)))
        self.assertEqual([], math.check_math(correct))

    def test_sans_serif_and_underline_are_valid_when_fully_closed(self):
        valid = [r'\(\underline{\textsf{still pending}}\)',
                 r'\(\textsf{\underline{still pending}}\)']
        broken = [r'\(\underline{\textsf{still pending}\)',
                  r'\(\textsf{\underline{still pending}\)']
        for expression in valid:
            self.assertEqual([], math.check_math(expression))
        for expression in broken:
            self.assertTrue(any('KaTeX parse error' in error for error in math.check_math(expression)))

    def test_quoted_and_code_evidence_is_not_authored_math(self):
        text = '> \\(\\textsf{C#}\\)\n\n`\\(broken`\n\n```tex\n\\(broken\n```\n\nOrdinary C#, 54%, sample_tool and $5.'
        self.assertEqual([], math.check_math(text))
        self.assertEqual([], math.check_math(r'\\(literal escaped delimiters\\)'))
        self.assertEqual([], math.check_math('> \\underline{\\textsf{quoted}}\n\n`\\underline{\\textsf{inline code}}`'))

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
