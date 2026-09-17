# Copyable response recipes

Use these recipes when drafting question reminders or when unsure about a recurring formatting choice. Keep words and meaning specific to the task; reuse the syntax instead of inventing another format.

## Rainbow question reminders

Use rainbow only for the short quoted user-question reminder above ⮑. Preserve the user's wording and perspective. Leave the full annotation/evidence block, source viewers, code, links, answer and About footer under their existing rules. These colours identify quoted context; they do not mean success, warning or failure. The quote is the explicit exception to semantic colour meanings and self-contained highlight chunks.

Use exactly one colour per word, with this fixed 24-step lookup table. For each new quote, the helper reserves the next starting index from 0–23, then uses `(start_index + word_index) % 24`. Wrap from the last colour back to the first. Continue across spaces and line wraps without resetting. Short quotes show only part of the cycle; do not stretch a cycle to fill the text. Pink connects purple back to red.

| Steps | Colours in order |
| --- | --- |
| 1–6 | `#fa7070` → `#fa9370` → `#fab570` → `#fad870` → `#fafa70` → `#d8fa70` |
| 7–12 | `#b5fa70` → `#93fa70` → `#70fa70` → `#70fa93` → `#70fab5` → `#70fad8` |
| 13–18 | `#70fafa` → `#70d8fa` → `#70b5fa` → `#7093fa` → `#7070fa` → `#9370fa` |
| 19–24 | `#b570fa` → `#d870fa` → `#fa70fa` → `#fa70d8` → `#fa70b5` → `#fa7093` |

Copy `\(\color{#fa7070}{\textsf{Word}}\)` for each word, changing only the lookup colour and escaped word. It ends in **two closing braces**, with no underline or size command. Separate expressions with ordinary spaces so the quote can wrap. Do not use per-letter markup, combine words into phrases, or place the whole quote inside one math expression. Punctuation attached to a word stays with it; each whitespace-delimited word advances one palette position.

Keep a single word, identifier or URL longer than 24 visible characters in inline code rather than a wide math box, and still advance the palette position for it. Prefer a genuinely shorter relevant excerpt to colouring a whole message. A helper avoids reconstructing syntax, but the emitted LaTeX still consumes output tokens; keep reminders short.

### Generate without reconstructing the syntax

Save the relevant excerpt in a UTF-8 plain-text file, then run:

```sh
python3 /path/to/response-preferences/scripts/rainbow-quote.py /tmp/question-1.txt /tmp/question-2.txt
```

Omit `--start-index` for normal use. For every final reply, collect its short question excerpts first and pass all their files to **one invocation** in display order. The helper takes the lock once, reads the next index, reserves one consecutive start per input file, and saves `(index + number_of_quotes) % 24`; each printed blockquote is separated by a blank line. State lives at `$CODEX_HOME/state/response-preferences/rainbow-next-index.txt` (default `~/.codex/state/...`), outside the published skill. A lock and atomic replacement protect concurrent tasks. The first quote starts at 0; successive reservations cycle through all 24 colours. This needs no model decision, network call, repeated process launch or per-quote state write. Concurrent tasks may display replies out of reservation order; a failed generation may consume positions. Reuse the generated quote unchanged on retries. Use `--start-index 0` (or another index through 23) only for reproducible examples/tests; with several files it assigns consecutive starts from that pinned index and does not advance the counter. This changes existing colour values without adding markup or another agent step.

The helper handles word colours and TeX escaping, validates the generated expressions with bundled KaTeX, and prints a Markdown blockquote to copy unchanged. No network or new integration is involved. It normalises whitespace to ordinary spaces, preserving the words and punctuation. Append any context link **outside** the colour expressions. Use `--format html` only for website examples; it escapes HTML and uses the same words and palette.

The general reply checker excludes quoted evidence, including historical broken syntax; it therefore does **not** validate the new formatting inside a quote. Use the helper, or validate the authored expressions directly with `math-validation.py`'s `render_errors`. This does not alter literal quoted evidence or add another automatic guard.

### Different lengths

These synthetic questions use the same word-by-word rhythm. The long example demonstrates the repeat after word 24.

```latex
> \(\color{#fa7070}{\textsf{Why?}}\)
```

```latex
> \(\color{#fa7070}{\textsf{Can}}\) \(\color{#fa9370}{\textsf{you}}\) \(\color{#fab570}{\textsf{make}}\) \(\color{#fad870}{\textsf{this}}\) \(\color{#fafa70}{\textsf{easier}}\) \(\color{#d8fa70}{\textsf{to}}\) \(\color{#b5fa70}{\textsf{read?}}\)
```

```latex
> \(\color{#fa7070}{\textsf{Can}}\) \(\color{#fa9370}{\textsf{you}}\) \(\color{#fab570}{\textsf{keep}}\) \(\color{#fad870}{\textsf{this}}\) \(\color{#fafa70}{\textsf{rainbow}}\) \(\color{#d8fa70}{\textsf{flowing}}\) \(\color{#b5fa70}{\textsf{through}}\) \(\color{#93fa70}{\textsf{a}}\) \(\color{#70fa70}{\textsf{longer}}\) \(\color{#70fa93}{\textsf{question,}}\) \(\color{#70fab5}{\textsf{so}}\) \(\color{#70fad8}{\textsf{I}}\) \(\color{#70fafa}{\textsf{can}}\) \(\color{#70d8fa}{\textsf{see}}\) \(\color{#70b5fa}{\textsf{how}}\) \(\color{#7093fa}{\textsf{the}}\) \(\color{#7070fa}{\textsf{colours}}\) \(\color{#9370fa}{\textsf{repeat}}\) \(\color{#b570fa}{\textsf{and}}\) \(\color{#d870fa}{\textsf{wrap}}\) \(\color{#fa70fa}{\textsf{onto}}\) \(\color{#fa70d8}{\textsf{another}}\) \(\color{#fa70b5}{\textsf{line}}\) \(\color{#fa7093}{\textsf{without}}\) \(\color{#fa7070}{\textsf{changing}}\) \(\color{#fa9370}{\textsf{their}}\) \(\color{#fab570}{\textsf{rhythm?}}\)
```

## Other recurring choices

| Situation | Reuse this decision |
| --- | --- |
| A saved/merged/deployed result | Green on the short confirmed outcome; ordinary details follow. |
| Useful explanation of how it works | Cyan on a complete short clause; do not turn it green merely because the task is finished. |
| Automated test result | 🧪 and ordinary text, with an explicit passed/failed/unverified status. |
| Needs the user's next action / mainly a takeaway | Favour 🫵 / 👉 respectively, normally once and only in the final reply. |
| One statement / several blocks | Inline marker / standalone marker plus the existing raised chevron. Keep ⮑ beside its answer in either case. |
| Technical punctuation in prose | Keep the identifier or number in inline code/ordinary text; underline the readable context around it. The quote helper can safely escape short literals. |
| Returning after hours | Final-only About: concrete subject, then one useful result or next step; split into short lavender expressions. |

For ordinary underlined prose, always keep the words in text mode: copy `\(\underline{\textsf{Words with spaces}}\)`. Keep the entire command between that one opening and one closing delimiter; the ending is exactly `}}\)`, with no extra backslash. Do not use `\(\underline{Words with spaces}\)`; KaTeX treats those words as maths, removes the spaces and italicises the letters.

```latex
\(\huge\text{✅}\) \(\color{#22c55e}{\textsf{\underline{The change is saved.}}}\)

\(\huge\text{ⓘ}\) \(\color{#67e8f9}{\textsf{\underline{Quotes use short colour chunks.}}}\)

\(\huge\text{🧪}\) The \(\underline{\textsf{formatter checks passed}}\), including C#, 54% and `sample_tool`.

\(\huge\text{👉}\) \(\underline{\textsf{The quote keeps your wording}}\); its colours identify the question being answered.

\(\color{#b8a4d9}{\textsf{About: Rainbow question reminders.}}\) \(\color{#b8a4d9}{\textsf{Fixed chunks keep longer quotes readable.}}\)
```

For a working update, replace the enlarged marker with its plain Unicode symbol, omit the finger and omit About. These are alternative snippets, not a requirement to include every category in one message. Underline the subject first and preserve negatives: “The upload is **still pending**” must not become a success cue merely because other work finished.
