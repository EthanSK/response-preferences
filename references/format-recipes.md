# Copyable response recipes

Use these recipes when drafting question reminders or when unsure about a recurring formatting choice. Keep words and meaning specific to the task; reuse the syntax instead of inventing another format.

## Rainbow question reminders

Use rainbow only for the short quoted user-question reminder above ⮑. Preserve the user's wording and perspective. Leave the full annotation/evidence block, source viewers, code, links, answer and About footer under their existing rules. These colours identify quoted context; they do not mean success, warning or failure. The quote is the explicit exception to semantic colour meanings and self-contained highlight chunks.

Use this fixed sequence, restarting for each quote:

`#f87171` red → `#fb923c` orange → `#facc15` yellow → `#4ade80` green → `#22d3ee` cyan → `#60a5fa` blue → `#c084fc` violet.

Copy `\(\color{#f87171}{\textsf{Your words}}\)` for each chunk, changing only its approved colour and escaped words. It ends in **two closing braces**, with no underline or size command. Separate expressions with ordinary spaces so the quote can wrap. Never put the entire rainbow inside one math expression. Use word boundaries, no per-letter markup, animation, gradient commands, or invented words to fill the palette. A one-word quote has one colour; short quotes need not contain every colour.

For consistent lengths, distribute the words as evenly as possible over seven chunks (one word per chunk if fewer than seven). Use more chunks when needed to keep each at three words or fewer. Split sooner if adding the next word would exceed 24 visible characters. Cycle the palette if needed. Keep a single longer identifier or URL in ordinary inline code rather than a wide math box. Prefer a genuinely shorter relevant excerpt to colouring a whole message.

### Generate without reconstructing the syntax

Save the relevant excerpt in a UTF-8 plain-text file, then run:

```sh
python3 /path/to/response-preferences/scripts/rainbow-quote.py /tmp/question.txt
```

The helper handles chunking and TeX escaping, validates the generated expressions with bundled KaTeX, and prints a Markdown blockquote to copy unchanged. No network or new integration is involved. It normalises whitespace to ordinary spaces, preserving the words and punctuation. Append any context link **outside** the colour expressions. Use `--format html` only for website examples; it escapes HTML and uses the same chunks and palette.

The general reply checker excludes quoted evidence, including historical broken syntax; it therefore does **not** validate the new formatting inside a quote. Use the helper, or validate the authored expressions directly with `math-validation.py`'s `render_errors`. This does not alter literal quoted evidence or add another automatic guard.

### Different lengths

These are synthetic example questions. Copy the source syntax; rendered colour still depends on the chat client.

```latex
> \(\color{#f87171}{\textsf{Can}}\) \(\color{#fb923c}{\textsf{you}}\) \(\color{#facc15}{\textsf{make}}\) \(\color{#4ade80}{\textsf{this}}\) \(\color{#22d3ee}{\textsf{easier}}\) \(\color{#60a5fa}{\textsf{to}}\) \(\color{#c084fc}{\textsf{read?}}\)
```

```latex
> \(\color{#f87171}{\textsf{Can you}}\) \(\color{#fb923c}{\textsf{show me}}\) \(\color{#facc15}{\textsf{how the}}\) \(\color{#4ade80}{\textsf{quoted question}}\) \(\color{#22d3ee}{\textsf{looks when}}\) \(\color{#60a5fa}{\textsf{it is}}\) \(\color{#c084fc}{\textsf{slightly longer?}}\)
```

```latex
> \(\color{#f87171}{\textsf{What happens if}}\) \(\color{#fb923c}{\textsf{we supply a}}\) \(\color{#facc15}{\textsf{type that's not}}\) \(\color{#4ade80}{\textsf{compatible with the}}\) \(\color{#22d3ee}{\textsf{DTO class? Is}}\) \(\color{#60a5fa}{\textsf{it just a}}\) \(\color{#c084fc}{\textsf{runtime error?}}\)
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

```latex
\(\huge\text{✅}\) \(\color{#22c55e}{\textsf{\underline{The change is saved.}}}\)

\(\huge\text{ⓘ}\) \(\color{#67e8f9}{\textsf{\underline{Quotes use short colour chunks.}}}\)

\(\huge\text{🧪}\) The \(\underline{\textsf{formatter checks passed}}\), including C#, 54% and `sample_tool`.

\(\huge\text{👉}\) \(\underline{\textsf{The quote keeps your wording}}\); its colours identify the question being answered.

\(\color{#b8a4d9}{\textsf{About: Rainbow question reminders.}}\) \(\color{#b8a4d9}{\textsf{Fixed chunks keep longer quotes readable.}}\)
```

For a working update, replace the enlarged marker with its plain Unicode symbol, omit the finger and omit About. These are alternative snippets, not a requirement to include every category in one message. Underline the subject first and preserve negatives: “The upload is **still pending**” must not become a success cue merely because other work finished.
