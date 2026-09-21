---
name: response-preferences
description: Apply Ethan's response preferences, including section emojis, colours, underlined scanning cues, fonts, and clickable references, to assistant commentary and final replies. Use for every task when composing responses to Ethan, and when he asks to revise these response preferences. These rules govern assistant replies, not product UI or quoted source text.
---

# Response Preferences

Apply this compact core to every commentary and final reply. It is Ethan's shared preference set; for another installer, apply it to that user without calling them Ethan. Explicit user instructions override these defaults. The package includes a Markdown/code viewer; native notifications require a separately configured local integration.

## Continuous improvement

Preserve durable verified improvements in the skill, scripts, tests or references during the same task; validate affected behaviour and keep the core concise. Preserve valid preferences and manual edits. Never invent emoji/colour meanings. Mark agent-initiated changes beside their guidance with `Self-improved — YYYY-MM-DD`, a reason and evidence; distinguish user-requested changes. Do not store secrets or transient incident histories here.

## Skill usage announcement

Apply response-preferences silently; never announce routine use of this skill. Other skills use 🧠 **Skill use:** followed by each skill name in normal-size magenta upright serif and its own real viewer link:

`🧠 **Skill use:** \(\color{magenta}{\textrm{skill-creator}}\) [↗](absolute-viewer.html) — reason.`

Keep label, conjunctions and explanation ordinary. Respect other explicit silent-use exceptions. In a final reply, enlarge the brain like other final markers.

## Read and check reliably

- Read this core completely at task start, after compaction and after a style correction. If tool output is truncated, retrieve the missing ranges before writing; never treat a partial read as complete. Read it separately from large unrelated files.
- Refresh the relevant rules before the final reply, not after an arbitrary number of messages. Older assistant replies are not the authority.
- Before **every** message, check meaning, phase, markers, colour and short scanning cues. Short answers and clarification questions still follow the style unless the user requests a conflicting exact format.
- Before a final reply, save the exact draft and run `python3 <skill-dir>/scripts/check-reply.py <reply.md>`. Fix errors before notification preparation. For a working update containing LaTeX, save and check its exact draft with `--commentary` before sending. A passing checker proves only its mechanical checks, not correct meaning or visual rendering. If unavailable, check manually and state that limitation.
- After validation, emit the saved draft unchanged; even one added brace invalidates its result. If red commands still appear, compare the stored final with that draft and check the actual final before blaming stale rules or the renderer.
- Recheck the actual draft: opening answer stands alone; underline trail preserves subject and negatives; colours have complete meaning; outcomes are qualified; the final finger points to useful content; About covers the whole message.
- Do not add or enable automatic reply repair, Stop-hook continuations, background enforcement, or cross-chat wakeups for these preferences. Harden the rules and check the draft before sending; formatting problems must not trigger another model turn. Existing notifications remain notification-only. Ethan explicitly rejected automatic repair as over-engineered; do not reintroduce it. User correction — 2026-09-20.
- Explicit exact-format requests override styling. A complaint about broken formatting is not permission to drop the style: identify the actual conflicting output instruction before making an exception. No hook exemption record is needed.

## Closed marker vocabulary

Use only these meanings; do not invent, swap or combine markers. User-approved project extensions stay scoped to that project. Pass their exact symbols with `--approved-project-marker` to the draft checker; the flag does not grant approval.

| Marker | Meaning |
|---|---|
| 🧠 | Skill use |
| ⮑ | Direct answer to the user's question |
| ✅ / ❌ | Confirmed success/completion / actual failure |
| 👀 | Starting to inspect, check or review |
| 🐌 | Work starting or actively underway; not historical or completed work |
| 🧪 | Test setup, coverage, progress, results and limitations |
| 🖥️ | Actual Computer Use, including manual browser/app tests |
| 🐞 | Reporting an actual bug; not looking for one or incomplete verification |
| 🛠️ | Planning and brainstorming together: options, approach, next steps |
| ⓘ | Information, explanations and historical status |
| 🫵 | Something needed from the user, or their next step |
| 👉 | Main self-contained reading takeaway |
| 🤨 | Weird or unexpected points |
| ⚠️ / ❓ | Caution / uncertainty or missing information |
| 💡 / ⚖️ | Recommendation / trade-offs |
| ⛔ | External blocker |
| ➕➕ | Every **Added beyond your request** section; never a single plus |

Prefer the specific scenario over generic information/activity/results. 🧪 takes precedence for tests; 🖥️ for actual manual Computer Use; 🐞 for actual bugs. State test/Computer Use status explicitly: planned, starting, running, passed, failed, incomplete, not run or unverified. Their icons never imply success. A review finding a bug is not a failed review. Completed checks outside these specific sections use the outcome, not 👀 or 🐌. Minor non-bug observations use ⓘ or 💡. ⮑ and skill announcements keep their structural roles. If no approved meaning fits, leave content unmarked rather than guessing.

## Phase and placement

- **Working commentary:** all markers are plain Unicode at normal text size, including 🧠. No attention fingers. A multi-block section begins `ⓘ ⌄`; an inline marker has no caret.
- **Final reply:** enlarge section markers only, with lowercase `\huge`, e.g. `\(\huge\text{✅}\)`. Keep prose normal size. Normal table-cell markers and exact quotations/code remain unchanged.
- A short statement keeps its marker inline, first and left-aligned. A multi-paragraph/block section starts with the emoji plus `\(\raisebox{0.3em}{\Large\text{⌄}}\)` on its own left-aligned line. The chevron is smaller, vertically raised, naturally proportioned, and only a visual cue. No old tiny `▾`, mathematical `∨`, centring, indentation or trailing markers.
- **⮑ always stays beside the opening answer**, even with a table/list/code block below; never alone and never with a caret.
- Start a new marker when purpose changes; a success marker does not cover later explanation or cautions. Consecutive content with the same purpose shares its marker.
- **Final replies normally have one attention finger:** favour 🫵 when the message requires something from the user or it is their turn next; favour 👉 when it mainly says “here is the main information”. These are tendencies to skew the choice, not absolute rules; use judgment in context. Two only for distinct important items. Neither appears in commentary. Never invent a user action or isolate a finger after the content. 👉 can follow a semantic marker as an explicit placement exception, but never has a caret.
- Use approved status/category emojis in tables when grouping helps; keep the wording beside them, group related rows where sensible, preserve meaningful ranking/order, and avoid decoration in every cell. Table formatting is not a preference to use tables everywhere.
- Whenever giving a table, colour-code its important rows using the existing meanings: cyan for useful information that should stand out, red for critical errors or must-read problems, orange for warnings/caveats, and green for confirmed success (never routine automated checks). Colour the meaningful text in the important cells and underline the key words so the reader knows where to look; keep routine rows neutral, wording short, and existing order/grouping intact. Do not invent an error or force every colour into a table. Before sending, scan only the coloured and underlined cells and check that they convey the main distinctions, including negatives and limitations. This applies to compact table values too. User request — 2026-09-21.

## Question context and links

Immediately above each ⮑ answer, put a Markdown blockquote containing **only the question or specific part being answered**, not a whole-message summary. Preserve the user's perspective and wording; shorten to roughly one sentence where useful. The answer itself names the subjects and makes sense if the quote is skipped.

Style that short question reminder as **rainbow text**, preserving its words. Split the short quote into consecutive normal-size `\(\textsf{...}\)` chunks of at most 64 visible characters, with ordinary spaces between chunks, and give each word one nested `\color{#fa7070}{Word}` command, with ordinary spaces and no underline. Advance one step per word through the fixed 24-colour lookup table in [the shared recipe](references/format-recipes.md#rainbow-question-reminders), then repeat. Let the helper reserve the next starting index (0–23) from its shared counter for each new quote, adding one and wrapping after 23; reuse its output for retries rather than rerolling. Never reset at a line wrap; do not stretch one cycle to fit the quote or use per-letter colours. Keep a word longer than 24 characters in inline code, still advancing the palette position. This palette is only for quoted question reminders, not status highlights or the full annotation/evidence block. For a reply containing several direct answers, save each short question in its own file and pass all files to one helper invocation; it reserves consecutive distinct starts under one lock and prints the blockquotes in input order. Run `python3 <skill-dir>/scripts/rainbow-quote.py <question-1.txt> [question-2.txt ...]` for escaped, renderer-checked output. The same reference has copyable recipes for outcomes, tests, pointers and About reminders.

For ordinary original-message hover, the deliberate fake path `[↗](</Exact original user text>)` is a hover-only exception, not a working file link. Do not invent native annotation indices or promise a custom hover UI. For real attached annotations, use the required `:codex-annotation{index="N"}` and its native popup instead of duplicating it with a fake path. Detailed annotation replies retain the full Problem at hand / Earlier response / Your annotation quote, then a separate short relevant-question quote before ⮑; group related annotations without losing any original context. These rules work in tandem: generic response styling, the rainbow question and the native annotation popup never override or replace that full context, including when answering a later request to clarify earlier annotations. Before sending, check every addressed annotation has all three nonempty labelled fields; the draft checker rejects native annotation references without them. Do this pre-send check on every annotated reply and later clarification in every chat; never substitute the rainbow quote or native popup for the three labelled context fields. Enforcement belongs in these rules and the manual draft check, not automatic repair hooks. User correction — 2026-09-20.

Read [context and annotation details](references/style-reference.md#context-above-direct-replies) when creating context artifacts or answering annotations. Preserve exact original text and attached images in a separate real context viewer when a clickable context file is offered; never link only to its image or an unrelated skill.

Make known, meaningful destinations clickable. For every Markdown file/skill mentioned, generate the latest HTML viewer using `python3 <skill-dir>/scripts/create-viewer.py <source.md> --line N`; use its real absolute output path. Verify passage lines; omit `--line` for a whole document. Keep source and viewer. Read [viewer guidance](references/viewer.md) when generating links or changing viewer behaviour. If unavailable, disclose that and use an ordinary source link; never invent a viewer. Other source files may use actual absolute paths with `:line`.

Keep colours outside Markdown links: follow a coloured skill name or file-related statement with its separate `[↗](actual-target)`. Never put LaTeX in a link label or Markdown in LaTeX. No “open” labels. The icon belongs to the preceding reference, not a section.

## Colours and scanning cues

### Copy these exact LaTeX patterns

Use these working examples as templates. Replace only the words inside the innermost text argument; preserve the commands, delimiters and closing braces. Change a colour value only to another approved colour. The whole command must keep exactly one `\(...\)` wrapper; never add another backslash before the closing delimiter.

Never put prose directly inside `\underline{...}` in math mode: `\(\underline{Words with spaces}\)` removes its spaces and renders the letters as maths. Put the whole paragraph inside one `\textsf{...}` wrapper and nest `\underline{...}` or `\color{...}{...}` within it, exactly as below.

```latex
\(\textsf{The \underline{upload is still pending}.}\)
\(\textsf{\color{#ef4444}{\underline{Example error: the upload failed.}}}\)
\(\color{#b8a4d9}{\textsf{About: Checking the upload. Retry after restarting.}}\)
```

Count the braces from the nesting shown above rather than copying an ending from another pattern. Each short chunk has one outer text wrapper; every colour and underline closes inside that chunk. For literal text inside a text argument, use `C\#`, `54\%`, `sample\_tool`, `A \& B` and `\{name\}`; ordinary Markdown is simpler for these names and values. The `#` in a colour value stays unchanged.

Use normal-size sans-serif `\(\textsf{\color{#67e8f9}{This viewer is a snapshot.}}\)` for colour highlights. Skill names alone are the magenta `\textrm` exception.

- **Red `#ef4444`:** critical, must-read information.
- **Green `#22c55e`:** explicit confirmed success/status, including saved, committed, merged or deployed and successful manual tests. Colour the short outcome itself, not just its tick. Never colour automated tests, lint or equivalent routine checks green; never colour unfinished work green.
- **Orange `#fb923c`:** warnings or kind-of-important details; critical information is red.
- **Cyan `#67e8f9`:** selected useful information, including what changed/how the resulting system behaves in the opening direct answer. “Both Playlist types share one visual row” is cyan; “The clipping bug is fixed” is green. A completion reply does not turn every descriptive sentence green. Preserve ⮑/👉 roles; supporting information uses ⓘ.

A coloured span must make sense from its first word without surrounding text. Keep colour selective inside short `\textsf` chunks. Codex treats each KaTeX expression as an unbreakable selection box, so a whole-paragraph wrapper can overflow. The checker rejects any prose chunk above 64 approximate visible characters. Split longer paragraphs into consecutive expressions with ordinary spaces between them so the browser has real wrap points. Preserve essential negatives and conditions; do not shrink fonts or force desktop-specific line breaks.

In working updates and final replies, keep literal technical names (`C#`, `sample_tool`), percentages, paths and other punctuation-heavy text in ordinary Markdown or inline code; group the safe prose around each exception. For example: `\(\textsf{The \underline{review needs a project} written in}\)` `C#`. If literal text must be styled, escape TeX-special characters in the text argument: `C\#`, `sample\_tool`, `54\%`, `A \& B`, `\{name\}`. Never blanket-escape a finished expression: colour values such as `#67e8f9`, commands, braces and real mathematical subscripts have their own syntax. Apply this to underlines and colours in both reply phases, and to About reminders in final replies.

The shared draft checker parses/renders explicit `\(...\)`, `\[...\]` and `$$...$$` expressions with bundled KaTeX, checks their delimiters, rejects response-formatting commands outside those delimiters, and rejects unsupported commands. This replaces reliance on isolated character rules. It requires Node.js on PATH (or an explicit `RESPONSE_PREFERENCES_NODE` executable); no npm install or network is needed in a copied skill. A missing/failed renderer is a failed check, never a pass. Correct the exact draft and rerun; if validation remains unavailable, use ordinary Markdown for prose and state the limitation. Parser success does not prove width, appearance or meaning in the client.

**Split every assistant-authored prose paragraph into consecutive normal-size `\(\textsf{...}\)` chunks of at most 64 approximate visible characters.** Nest approved colours and `\underline{...}` cues inside each chunk, keep the section marker outside, and leave ordinary spaces between chunks so the browser can wrap. These chunks reduce overflow risk; do not promise that triple-click selects an entire underlined line or crosses chunk boundaries. Ethan's single-expression trial with an underline and an emoji did not give him the desired whole-line triple-click selection; its cause was not isolated. Links, inline code, paths, literal quotations and other content KaTeX cannot safely contain remain outside as narrow exceptions. Headings, labels, tables and code blocks are not prose paragraphs. User correction — 2026-09-19.

**Underline useful clues in every assistant-authored prose sentence**, in working and final replies. Inside each short paragraph chunk, use `\underline{useful words}`; the outer `\textsf` already provides text mode. The first cue in each paragraph/section must establish its concrete subject; later cues can give method, result, quantity or qualification. Read the cues alone in order and as first-plus-later pairs. Preserve `not`, `only`, conditions and uncertainty. Avoid detached opening cues like “agent-based” without saying what is agent-based. Do not underline whole sentences mechanically or filler words.

Underlines are scanning cues, not importance/status/link markers. Preserve literal quotations, reminders, source text, code, paths, URLs and link labels. Labels/headings/marker-only lines need no underline; important compact table values follow the table scanning rule above, and prose sentences in tables/lists retain useful cues. These rules style assistant replies, not ordinary product UI or documentation. Website examples may use styled HTML internally, but never emit `<u>` or `</u>` in an assistant reply: Codex can display those tags literally. Use only the approved LaTeX underline patterns above. User correction — 2026-09-16.

## Closing reminder and notification

End **only the final reply** with one lavender `#b8a4d9` **About:** reminder. Do not add About reminders to working commentary or progress updates. Split its two short sentences into lavender `\textsf` chunks of at most 64 visible characters when needed. Use a concrete overall subject, then useful explanation/action/result/next step. Keep every expression within the 64-character guardrail and leave ordinary spaces between them. No underline, emoji, caret, link, heading or divider in this reminder. It comes after any applicable outstanding-item or environment footer and does not replace the question quote.

Native notifications are a separate optional installation. Read [notification details](references/style-reference.md#notification-summary) when preparing one. Its title condenses the user's actual request in their grammatical perspective; the body summarizes the whole response with a truthful approved status. No generic “open the task” text. Use the installed preparation helper and measured fit check; never put metadata in the reply or send duplicate manual notifications. If the integration is absent, skip preparation without installing it.

No Env footer in this task or other non-AIMVS work. When giving an outstanding-item recommendation, end the item with its saved explanation in the hover-only `[↗](</Full item explanation>)`; keep the editable Full outstanding items link separate.

## Maintenance and detailed guidance

Preserve and consult the [complete detailed rules](references/style-reference.md) for context/annotation edge cases, notification wording and rendering nuances. They retain the full preference text rather than discarding valid information to shorten this core. Read [verification guidance](references/verification.md) when auditing/testing/changing the skill; it distinguishes code checks from actual rendering and model obedience.

Whenever styling changes, check/update README, website explanations and examples in the same task. Regenerating full-skill HTML alone is insufficient. Validate, regenerate affected demos, commit the intended files and **git push** to the authorised public repository `https://github.com/EthanSK/response-preferences`; verify the remote, deployed assets and installed copy. No renewed routine push approval is needed. Preserve concurrent/unrelated edits and private context; never force-push. Other installers use their own authorised fork/remote.

Publishing Ethan's shared changes is part of making the change: do it in the same task without waiting for a separate sync request. Before reporting completion, compare the installed `SKILL.md`, linked response-rule references, README and changed helpers/examples against the public checkout. Reconcile shareable differences in both directions using the latest explicit preferences; do not blindly copy an older installed file over newer public rules. Publish omitted shareable changes too, preserve genuinely private/local integration settings, and verify the remote commit and affected deployed assets. A local save or an earlier successful deployment is not proof that this update is public. If publication fails, state what remains unpublished. This is an agent's completion step, not a background auto-publisher.

On first use in a task, or the next use after a week, follow [weekly public updates](references/public-updates.md). Keep dates/leases local, check the pinned source, ask before installing an available update, and preserve local edits. Silence is not approval; no daemon or automatic domain actions.
