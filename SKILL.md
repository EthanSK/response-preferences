---
name: response-preferences
description: Apply Ethan's response preferences, including section emojis, colours, underlined scanning cues, fonts, and clickable references, to assistant commentary and final replies. Use for every task when composing responses to Ethan, and when he asks to revise these response preferences. These rules govern assistant replies, not product UI or quoted source text.
---

# Response Preferences

Apply this compact core to every commentary and final reply. It is Ethan's shared preference set; for another installer, apply it to that user without calling them Ethan. Explicit user instructions override these defaults. The package includes a Markdown/code viewer; native notifications and automatic checking require separately configured local integrations.

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
- Before a final reply, save the exact draft and run `python3 <skill-dir>/scripts/check-reply.py <reply.md>`. Fix errors before notification preparation. For a working update containing LaTeX, save and check its exact draft with `--commentary` before sending. The automatic completion guard runs on final replies; it does not intercept working updates. A passing checker proves only its mechanical checks, not correct meaning or visual rendering. If unavailable, check manually and state that limitation.
- After validation, emit the saved draft unchanged; even one added brace invalidates its result. If red commands still appear, compare the stored final with that draft and check the actual final before blaming stale rules or the renderer. A guard receipt requesting repair is not evidence that a corrected reply appeared; follow [the failed-repair diagnostic](references/reliability.md#when-a-checked-draft-still-produces-red-commands).
- Recheck the actual draft: opening answer stands alone; underline trail preserves subject and negatives; colours have complete meaning; outcomes are qualified; the final finger points to useful content; About covers the whole message.
- The optional [automatic guard](references/reliability.md) checks finals even when the agent forgets. It can request one formatting-only continuation; it cannot hide streamed text, guarantee semantic choices or cover clients where it is not installed. Never promise perfect obedience.
- With that guard installed, read its exact-format exception procedure when the user explicitly requests undecorated output. Bind the exception to that task and exact reply; never use it merely to avoid styling.

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

## Question context and links

Immediately above each ⮑ answer, put a Markdown blockquote containing **only the question or specific part being answered**, not a whole-message summary. Preserve the user's perspective and wording; shorten to roughly one sentence where useful. The answer itself names the subjects and makes sense if the quote is skipped.

For ordinary original-message hover, the deliberate fake path `[↗](</Exact original user text>)` is a hover-only exception, not a working file link. Do not invent native annotation indices or promise a custom hover UI. For real attached annotations, use the required `:codex-annotation{index="N"}` and its native popup instead of duplicating it with a fake path. Detailed annotation replies retain the full Problem at hand / Earlier response / Your annotation quote, then a separate short relevant-question quote before ⮑; group related annotations without losing any original context.

Read [context and annotation details](references/style-reference.md#context-above-direct-replies) when creating context artifacts or answering annotations. Preserve exact original text and attached images in a separate real context viewer when a clickable context file is offered; never link only to its image or an unrelated skill.

Make known, meaningful destinations clickable. For every Markdown file/skill mentioned, generate the latest HTML viewer using `python3 <skill-dir>/scripts/create-viewer.py <source.md> --line N`; use its real absolute output path. Verify passage lines; omit `--line` for a whole document. Keep source and viewer. Read [viewer guidance](references/viewer.md) when generating links or changing viewer behaviour. If unavailable, disclose that and use an ordinary source link; never invent a viewer. Other source files may use actual absolute paths with `:line`.

Keep colours outside Markdown links: follow a coloured skill name or file-related statement with its separate `[↗](actual-target)`. Never put LaTeX in a link label or Markdown in LaTeX. No “open” labels. The icon belongs to the preceding reference, not a section.

## Colours and scanning cues

Use normal-size sans-serif `\(\color{#67e8f9}{\textsf{This viewer is a snapshot.}}\)` for colour highlights. Skill names alone are the magenta `\textrm` exception.

- **Red `#ef4444`:** critical, must-read information.
- **Green `#22c55e`:** explicit confirmed success/status, including saved, committed, merged or deployed and successful manual tests. Colour the short outcome itself, not just its tick. Never colour automated tests, lint or equivalent routine checks green; never colour unfinished work green.
- **Orange `#fb923c`:** warnings or kind-of-important details; critical information is red.
- **Cyan `#67e8f9`:** selected useful information, including what changed/how the resulting system behaves in the opening direct answer. “Both Playlist types share one visual row” is cyan; “The clipping bug is fixed” is green. A completion reply does not turn every descriptive sentence green. Preserve ⮑/👉 roles; supporting information uses ⓘ.

A coloured span must make sense from its first word without surrounding text. Keep it selective and short—aim around 40 visible characters or fewer, not whole sections or multi-sentence explanations. LaTeX prose is often unbreakable: use ordinary wrapping prose for details, and separate short expressions for underlines and About. The checker rejects expressions above 80 approximate visible characters; this is not a pixel-width guarantee. Preserve essential negatives/conditions; rewrite or leave uncoloured rather than clipping meaning. Do not shrink fonts or force desktop-specific line breaks.

In working updates and final replies, keep literal technical names (`C#`, `sample_tool`), percentages, paths and other punctuation-heavy text in ordinary Markdown or inline code; underline short readable words around them. For example: `The \(\underline{\textsf{review needs a project}}\) in C#.` If literal text must be styled, escape TeX-special characters in the text argument: `C\#`, `sample\_tool`, `54\%`, `A \& B`, `\{name\}`. Never blanket-escape a finished expression: colour values such as `#67e8f9`, commands, braces and real mathematical subscripts have their own syntax. Apply this to underlines, colours and About reminders in both reply phases.

The shared draft checker parses/renders explicit `\(...\)`, `\[...\]` and `$$...$$` expressions with bundled KaTeX, checks their delimiters and rejects unsupported commands. This replaces reliance on isolated character rules. It requires Node.js on PATH (or an explicit `RESPONSE_PREFERENCES_NODE` executable); no npm install or network is needed in a copied skill. A missing/failed renderer is a failed check, never a pass. Correct the exact draft and rerun; if validation remains unavailable, use ordinary Markdown for prose and state the limitation. Parser success does not prove width, appearance or meaning in the client.

**Underline useful clues in every assistant-authored prose sentence**, in working and final replies. Use normal-size `\(\underline{\textsf{useful words}}\)` or nest `\underline{...}` inside a coloured `\textsf` span. The first cue in each paragraph/section must establish its concrete subject; later cues can give method, result, quantity or qualification. Read the cues alone in order and as first-plus-later pairs. Preserve `not`, `only`, conditions and uncertainty. Avoid detached opening cues like “agent-based” without saying what is agent-based. Do not underline whole sentences mechanically or filler words. Keep spans short enough to wrap sensibly.

Underlines are scanning cues, not importance/status/link markers. Preserve literal quotations, reminders, source text, code, paths, URLs and link labels. Labels/headings/marker-only lines and compact table values need no underline; prose sentences in tables/lists do. These rules style assistant replies, not ordinary product UI or documentation; website example replies demonstrate them with `<u>`.

## Closing reminder and notification

End **every** commentary and final message with one lavender `#b8a4d9` **About:** reminder. Use two short sentences: a concrete overall subject, then useful explanation/action/result/next step. Avoid vague labels and repetition. Split into short normal-size sans-serif LaTeX expressions with ordinary spaces so it wraps. No underline, emoji, caret, link, heading or divider in this reminder. It comes after any applicable outstanding-item or environment footer and does not replace the question quote.

Native notifications are a separate optional installation. Read [notification details](references/style-reference.md#notification-summary) when preparing one. Its title condenses the user's actual request in their grammatical perspective; the body summarizes the whole response with a truthful approved status. No generic “open the task” text. Use the installed preparation helper and measured fit check; never put metadata in the reply or send duplicate manual notifications. If the integration is absent, skip preparation without installing it.

No Env footer in this task or other non-AIMVS work. When giving an outstanding-item recommendation, end the item with its saved explanation in the hover-only `[↗](</Full item explanation>)`; keep the editable Full outstanding items link separate.

## Maintenance and detailed guidance

Preserve and consult the [complete detailed rules](references/style-reference.md) for context/annotation edge cases, notification wording and rendering nuances. They retain the full preference text rather than discarding valid information to shorten this core. Read [verification guidance](references/verification.md) when auditing/testing/changing the skill; it distinguishes code checks from actual rendering and model obedience.

Whenever styling changes, check/update README, website explanations and examples in the same task. Regenerating full-skill HTML alone is insufficient. Validate, regenerate affected demos, commit the intended files and **git push** to the authorised public repository `https://github.com/EthanSK/response-preferences`; verify the remote, deployed assets and installed copy. No renewed routine push approval is needed. Preserve concurrent/unrelated edits and private context; never force-push. Other installers use their own authorised fork/remote.

On first use in a task, or the next use after a week, follow [weekly public updates](references/public-updates.md). Keep dates/leases local, check the pinned source, ask before installing an available update, and preserve local edits. Silence is not approval; no daemon or automatic domain actions.
