---
name: response-preferences
description: Apply Ethan's response preferences, including section emojis, colours, underlined scanning cues, and clickable references, to assistant commentary and final replies. Use for every task when composing responses to Ethan, and when he asks to revise these response preferences. These rules govern assistant replies, not product UI or quoted source text.
---

# Response Preferences

Apply this compact core to every commentary and final reply. It is Ethan's shared preference set; for another installer, apply it to that user without calling them Ethan. Explicit user instructions override these defaults. The package includes a Markdown/code viewer; native notifications require a separately configured local integration.

## Continuous improvement

Preserve durable verified improvements in the skill, scripts, tests or references during the same task; validate affected behaviour and keep the core concise. Preserve valid preferences and manual edits. Never invent emoji/colour meanings. Mark agent-initiated changes beside their guidance with `Self-improved — YYYY-MM-DD`, a reason and evidence; distinguish user-requested changes. Do not store secrets or transient incident histories here.

## Skill usage announcement

Apply response-preferences silently; never announce routine use of this skill. Other skills use 🧠 **Skill use:** followed by each skill name in normal-size magenta upright serif and its own real viewer link:

`🧠 **Skill use:** \(\textrm{\color{magenta}skill-creator}\) [↗](absolute-viewer.html) — reason.`

Keep label, conjunctions and explanation ordinary. Respect other explicit silent-use exceptions. In a final reply, enlarge the brain like other final markers.

## Read and check reliably

- Read this core completely at task start, after compaction and after a style correction. If tool output is truncated, retrieve the missing ranges before writing; never treat a partial read as complete. Read it separately from large unrelated files.
- Reread this core at least every five assistant messages, including commentary, and immediately before each final reply. Task start, compaction and a style correction still require an immediate complete read; restart the five-message count after that read. Before presenting or restating review findings, also reread the installed `code-review-findings` skill and the applicable project review contract. Older assistant replies are not the authority. User request — 2026-10-03.
- Draft relevant annotation answers in this order: the three nonempty quoted fields `Problem at hand` / `Earlier response` / `Your annotation`, the short rainbow question, then the answer. Compare the actual draft with the canonical source before sending, including Agent Flow selections without native annotation indices. When diagnosing an omitted Agent Flow context block, run the existing checker with `--require-annotation-context`; ordinary standalone questions retain their exception. User request — 2026-10-03.
- Before **every** message, check meaning, phase, markers, selected colours and short underlined clues sentence by sentence. Short answers and clarification questions still follow the phase's style unless the user requests a conflicting exact format.
- Keep underlines in working and final replies, including their sans-serif styling. Use the complete short `\(\underline{\textsf{clue with spaces}}\)` pattern below. The `\textsf` **inside that short underline stays**. Do not add a second, outer LaTeX wrapper around its surrounding sentence or paragraph for selection/grouping: that did not give Ethan whole-line triple-click selection and can overflow. Keep colours and About in their separate short patterns. User clarification — 2026-09-23.
- The bundled `scripts/check-reply.py` remains an optional diagnostic for a tricky draft or skill maintenance, not a step for every message. It detects syntax and structural mistakes but cannot make an agent use it or guarantee correct rendering. If red commands appear, inspect the exact emitted expression and compare it with the patterns below before changing the parser. Codex hides the `\(`/`\)` of an expression it cannot render, so red raw text alone does not prove the delimiters were missing; read the raw session text before diagnosing. Self-improved — 2026-09-24: a red `not 100% sure` cue was misdiagnosed as missing delimiters; the session log showed both delimiters and a bare `%`. Evidence: `LEARNINGS.md`, “Everyday percentages and hidden delimiters”. User-requested simplification — 2026-09-22.
- Recheck the actual draft: opening answer stands alone; underlined clues preserve subject and negatives; numbers and symbols stay visible; inside each styled text argument, write `10\%` and `\$500`, not bare `10%` or `$500`; colours have complete meaning; outcomes are qualified; the final finger points to useful content; About covers the whole message.
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
| 🖥️ | Actual Computer Use, including manual browser/app tests, and every **Manual checks** section |
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

Prefer the specific scenario over generic information/activity/results. 🧪 takes precedence for tests; 🖥️ for actual manual Computer Use and every **Manual checks** section; 🐞 for actual bugs. Use the computer emoji for manual checks: start each **Manual checks** section with 🖥️, including checks proposed for the user to run; it labels the section and never claims the agent ran them. Before sending, check every Manual checks heading has it. User request — 2026-10-04. State test/Computer Use status explicitly: planned, starting, running, passed, failed, incomplete, not run or unverified. Their icons never imply success. A review finding a bug is not a failed review. Completed checks outside these specific sections use the outcome, not 👀 or 🐌. Minor non-bug observations use ⓘ or 💡. ⮑ and skill announcements keep their structural roles. If no approved meaning fits, leave content unmarked rather than guessing.

## Phase and placement

- **Working commentary:** ordinary Markdown prose around short underlined clues and selected colour highlights. Markers are plain Unicode at normal text size, including 🧠. Exception: responses directly pointed at the user, the ⮑ direct answer, stay big with `\(\huge\text{⮑}\)` so things they should look out for stand out from working steps. User request — 2026-10-04. No attention fingers. A multi-block section begins `ⓘ ⌄`; an inline marker has no caret.
- **Final reply:** enlarge section markers only, with lowercase `\huge`, e.g. `\(\huge\text{✅}\)`. Keep prose normal size. Normal table-cell markers and exact quotations/code remain unchanged.
- A short statement keeps its marker inline, first and left-aligned. A multi-paragraph/block section starts with the emoji plus `\(\raisebox{0.3em}{\Large\text{⌄}}\)` on its own left-aligned line. The chevron is smaller, vertically raised, naturally proportioned, and only a visual cue. No old tiny `▾`, mathematical `∨`, centring, indentation or trailing markers.
- **⮑ always stays beside the opening answer**, even with a table/list/code block below; never alone and never with a caret.
- Start a new marker when purpose changes; a success marker does not cover later explanation or cautions. Consecutive content with the same purpose shares its marker.
- **Final replies normally have one attention finger:** favour 🫵 when the message requires something from the user or it is their turn next; favour 👉 when it mainly says “here is the main information”. These are tendencies to skew the choice, not absolute rules; use judgment in context. Two only for distinct important items. Neither appears in commentary. Never invent a user action or isolate a finger after the content. 👉 can follow a semantic marker as an explicit placement exception, but never has a caret.
- Use approved status/category emojis in tables when grouping helps; keep the wording beside them, group related rows where sensible, preserve meaningful ranking/order, and avoid decoration in every cell. Table formatting is not a preference to use tables everywhere.
- Whenever giving a table, colour-code its important rows using the existing meanings: cyan for useful information that should stand out, red for critical errors or must-read problems, orange for warnings/caveats, and green for confirmed success (never routine automated checks). Colour the meaningful text in the important cells and underline the key words so the reader knows where to look; keep routine rows neutral, wording short, and existing order/grouping intact. Do not invent an error or force every colour into a table. Before sending, scan only the coloured and underlined cells and check that they convey the main distinctions, including negatives and limitations. This applies to compact table values too. User correction — 2026-09-23.

## Question context and links

If referring to things you'll clarify later, do the clarification there and then; say “More clarification below” only when a later section adds detail. Explain the term and relevant limitation at first mention so each answer stands on its own, including every annotation answer and main or side chat reply. Before sending, read each answer without the later sections and move any clarification needed to understand it beside the original statement. User request — 2026-10-04.

Separate each distinct annotation-response section with a Markdown horizontal divider (`---`) from now on, including Agent Flow selections. Keep related annotations grouped when they share one answer; do not put dividers between that section's context, short question and answer. Before sending, check adjacent annotation answers have a divider between them. User request — 2026-09-28.

Immediately above each ⮑ answer, put a Markdown blockquote containing **only a short reminder of the question or specific part being answered**, not a whole-message summary. Favor wording that names what the user was talking about so it makes sense when they return later. Keep their perspective and wording where possible; when a pronoun or vague phrase hides the subject, lightly rephrase it or replace it with the concrete noun clearly established by the prompt and nearby context. For example, replace an unexplained “if it's like a one-time thing” with “Can we pause the whole hidden component at once?”. Do not guess an uncertain subject, insert the answer, or turn the reminder into a topic label. Keep the exact original wording in the annotation context/source. User request — 2026-10-04. Let the rainbow reminder be roughly double the former length: use around 60–80 visible characters when that much relevant wording exists, with a maximum of 80. Let it wrap naturally; do not shorten it just to fit one line. Keep naturally short questions short and retain only the relevant question, including its resolved subject, instead of padding or summarizing unrelated parts. User request — 2026-10-04. The answer itself names the subjects and makes sense if the quote is skipped. User correction — 2026-09-23. Respond to relevant Agent Flow selections plus Ethan's accompanying comments like normal annotations: keep all three fields, `Problem at hand` / `Earlier response` / `Your annotation`, before the short rainbow reminder and answer. This includes selected code and `app_selection` or `codex_selection` tags wrapped in coloured/escaped LaTeX, even without a native annotation directive. Do not reduce the block to only `Problem at hand` or add a separate square-bracket context note. Name what is being discussed, where it appears and why it came up. For selected code or another app's text, identify that source within `Earlier response` rather than attributing it to the assistant. Quote the selected text and the matching user comment faithfully; do not invent a connection or a native annotation directive. Ordinary standalone questions do not need a manufactured annotation block. Before sending, match each relevant selection to the actual user comment and verify that all three labelled fields appear before its answer; a rainbow question alone fails this check. This replaces the square-bracket context rule. User request — 2026-09-26; hardened at Ethan's request — 2026-09-27.

Style that short question reminder as **rainbow text** in main chats and side chats, using the authored words from the full prompt when supplied, with minimal subject clarification under the rule above. Keep it alongside the applicable `Problem at hand` / `Earlier response` / `Your annotation` fields; those fields never replace it. Before sending, check that the rainbow blockquote is immediately above ⮑. Read-only side-chat boundaries do not exempt response formatting; use the non-mutating helper invocation in [context guidance](references/style-reference.md#context-above-direct-replies). User correction — 2026-09-30. Use the `rainbow-quote.py` helper; do not hand-write its LaTeX. The normal helper rejects a complete excerpt over 80 visible characters before reserving any colour offsets; it splits the reminder into expressions of at most 64 visible characters so longer reminders can wrap. It emits normal-size sans-serif `\(\textsf{...}\)` with one colour per word. Advance one step per word through the fixed 24-colour lookup table in [the shared recipe](references/format-recipes.md#rainbow-question-reminders), then repeat; do not stretch one cycle to fit the quote or use per-letter colours. Let the helper reserve the next starting index (0–23) from its shared counter for each new quote, adding one and wrapping after 23; reuse its output for retries rather than rerolling. Keep a word longer than 24 characters in inline code, still advancing the palette position. This palette is only for quoted question reminders, not status highlights or the full annotation/evidence block. For a reply containing several direct answers, save each short question in its own file and pass all files to one helper invocation; it reserves consecutive distinct starts under one lock and prints the blockquotes in input order. Run `python3 <skill-dir>/scripts/rainbow-quote.py <question-1.txt> [<question-2.txt> ...]` for escaped, renderer-checked output. The same reference has copyable recipes for outcomes, tests, pointers and About reminders.

For ordinary original-message hover, the deliberate fake path `[↗](</Exact original user text>)` is a hover-only exception, not a working file link. Do not invent native annotation indices or promise a custom hover UI. For real attached annotations, use the required `:codex-annotation{index="N"}` and its native popup instead of duplicating it with a fake path. Detailed annotation replies retain the full Problem at hand / Earlier response / Your annotation quote, then a separate short relevant-question quote before ⮑; group related annotations without losing any original context. These rules work in tandem: generic response styling, the rainbow question and the native annotation popup never override or replace that full context, including when answering a later request to clarify earlier annotations. Before sending, check every addressed annotation has all three nonempty labelled fields; the draft checker rejects native annotation references without them. Do this pre-send check on every annotated reply and later clarification in every chat; never substitute the rainbow quote or native popup for the three labelled context fields. Enforcement belongs in these rules and the manual draft check, not automatic repair hooks. User correction — 2026-09-20.

Selections from Agent Flow (`codex_selection` blocks and annotations) are often just text the user highlighted while reading, so their count says nothing about how many things they are asking. Be smart about it: treat a selection as something to answer only when it matches what the user is actually saying or asking. Ignore selections that are clearly highlighted just for reading and do not match their words; do not answer, quote or list those. User request — 2026-09-26.

Read [context and annotation details](references/style-reference.md#context-above-direct-replies) when creating context artifacts or answering annotations. Preserve exact original text and attached images in a separate real context viewer when a clickable context file is offered; never link only to its image or an unrelated skill.

Make known, meaningful destinations clickable. For every Markdown file/skill mentioned, generate the latest HTML viewer using `python3 <skill-dir>/scripts/create-viewer.py <source.md> --line N`; use its real absolute output path. Verify passage lines; omit `--line` for a whole document. Keep source and viewer. Read [viewer guidance](references/viewer.md) when generating links or changing viewer behaviour. If unavailable, disclose that and use an ordinary source link; never invent a viewer. Copy the exact path printed by `create-viewer.py` and verify that file exists immediately before posting; never reconstruct its fingerprint or guess another skill’s path. If that output is truncated, rerun the helper with bounded output; never fill in an omitted path, and check each exact link target in the finished draft exists. Self-improved — 2026-10-04: a guessed viewer link failed the local existence check; the helper’s returned path passed (see [verification evidence](references/verification.md#viewer-link-existence)). Self-improved — 2026-10-05: truncated batched output prompted another guessed link; rerunning the helper supplied the real path (Codex task: 01a102b9-c087-7771-8748-8ee14c4c56e0). Other source files may use actual absolute paths with `:line`.

Keep colours outside Markdown links: follow a coloured skill name or file-related statement with its separate `[↗](actual-target)`. Never put LaTeX in a link label or Markdown in LaTeX. No “open” labels. The icon belongs to the preceding reference, not a section.

## Colours and scanning cues

### Copy these exact colour patterns

Use the complete short underline expression below for scanning. `\textsf{...}` keeps the sans-serif font and spaces; `\underline{...}` draws the line. It ends `}}\)`: one brace closes `\textsf`, one closes `\underline`. The colour pattern is separate and ends `}\)`. Keep each expression short enough to wrap around ordinary Markdown. User correction — 2026-09-23.

```latex
The upload is \(\underline{\textsf{still pending}}\).
\(\textsf{\color{#ef4444}The upload failed.}\)
\(\textsf{\color{#b8a4d9}About: Checking the upload.}\) \(\textsf{\color{#b8a4d9}Retry after restarting.}\)
```

Copy each complete pattern rather than assembling fragments or repairing its ending. Before sending, check that every assistant-authored `\(` expression has its closing `\)`: an underline ends `}}\)`, not just `}}`. Braces close the formatting commands; they do not close the math expression. User correction — 2026-10-05. Underline and colour stay in separate expressions. The final About expression is its own fixed pattern.

**Dollar signs and prices are allowed. Show the price the user needs and figure out the correct formatting without making them handle it.** Write `$500` in ordinary Markdown, or `\$500` inside an underline, colour or About expression; both display the dollar sign. For example, `\(\underline{\textsf{Pro \$500 upgrade grants access}}\)` keeps the price inside the styled cue. Do not omit a price, replace its currency or ban dollar signs to avoid a formatting error. User correction — 2026-10-09: replace the misleading ban with correct handling (see [price verification](references/verification.md#prices-in-styled-prose)).

### Keep literal symbols visible

**Allow ordinary symbols, especially percentages. Handle the escaping yourself; never prohibit, drop or change a number, unit, price or symbol just to make styling easier.** Inside an underline, colour or About text argument, use the lookup below. Outside LaTeX, ordinary Markdown keeps `10%` and `$500` unchanged. User-requested hardening — 2026-10-09; [rendering verification](references/verification.md#literal-symbols-in-styled-prose).

| Visible literal | Write inside styled text |
| --- | --- |
| `%` | `\%` |
| `$` | `\$` |
| `#` | `\#` |
| `_` | `\_` |
| `&` | `\&` |
| `{` / `}` | `\{` / `\}` |
| `~` | `\textasciitilde{}` |
| `^` | `\textasciicircum{}` |
| backslash | `\textbackslash{}` |

Copy the complete pattern, replacing only its literal text and escaping that text once. A bare `%` starts a TeX comment, hiding the remaining text and closing braces. `10\%` still displays **10%**, not the backslash. These two percentage cues preserve their wording:

```latex
\(\underline{\textsf{10\% cheaper than Balanced}}\)
\(\underline{\textsf{about 20\% lower compute-plus-transfer cost}}\)
\(\textsf{\color{#67e8f9}The price is \$99.95, down 10\%.}\)
```

Escape only literal text being inserted, never a finished expression: the `#` in `\color{#67e8f9}`, command backslashes, structural braces and real mathematical subscripts/superscripts keep their syntax. Do not double an existing escape. Keep code, paths, links and exact source quotations in their existing Markdown form; ordinary punctuation needs no invented escape.

Use normal-size `\(\textsf{\color{#67e8f9}This viewer is a snapshot.}\)` for colour highlights. Skill names alone are the magenta `\textrm` exception.

- **Red `#ef4444`:** critical, must-read information.
- **Green `#22c55e`:** explicit confirmed success/status, including saved, committed, merged or deployed and successful manual tests. Colour the short outcome itself, not just its tick. Never colour automated tests, lint or equivalent routine checks green; never colour unfinished work green.
- **Orange `#fb923c`:** warnings or kind-of-important details; critical information is red.

User request — 2026-10-04: Explain orange warnings, including orange `(sus)` points, in a bit more detail from first principles: remind me what feature or surface we are talking about, what should happen, what actually happens, and why it matters. State whether it is a confirmed bug, an intentional limitation or still unverified, and whether it was introduced here or already existed. Keep the short orange highlight self-contained and put the necessary explanation beside it in ordinary wrapping prose. Other routine information should stay less prominent; do not make everything stand out.
- **Cyan `#67e8f9`:** selected useful information, including what changed/how the resulting system behaves in the opening direct answer. “Both Playlist types share one visual row” is cyan; “The clipping bug is fixed” is green. A completion reply does not turn every descriptive sentence green. Preserve ⮑/👉 roles; supporting information uses ⓘ.

A coloured span must make sense from its first word without surrounding text. Keep each colour highlight short and self-contained. Codex treats each KaTeX expression as an unbreakable selection box, so leave the rest of the sentence as wrapping Markdown. Keep every expression below 64 approximate visible characters; split a long highlight into separate short thoughts or leave it uncoloured. Preserve essential negatives and conditions.

In working and final replies, short cues may include percentages, prices and literal names using the symbol lookup above. Ordinary Markdown remains useful for surrounding prose; paths, code, links and exact quotations retain their own formatting. Keep each styled expression short so it can wrap beside that prose.

The optional diagnostic checker parses/renders explicit `\(...\)`, `\[...\]` and `$$...$$` expressions with bundled KaTeX, checks their delimiters, rejects response-formatting commands outside those delimiters, and rejects unsupported commands. This replaces reliance on isolated character rules. It requires Node.js on PATH (or an explicit `RESPONSE_PREFERENCES_NODE` executable); no npm install or network is needed in a copied skill. A missing/failed renderer is a failed diagnostic, never a pass. Correct that draft if you invoke it; ordinary Markdown remains the safe fallback. Parser success does not prove width, appearance or meaning in the client.

**Write prose as ordinary Markdown around short expressions.** Use `\(\underline{\textsf{short useful words}}\)` for sans-serif scanning and the separate `\(\textsf{\color{#67e8f9}A complete short fact.}\)` when colour helps. The inner `\textsf` styles the underlined clue; it is not the rejected whole-sentence grouping wrapper. A coloured sentence already carries the scanning message; do not repeat it solely to add an underline. Keep expressions short enough to fit, with ordinary spaces around them for wrapping. User clarification — 2026-09-23.

**Use a short, useful underlined clue in each substantive assistant-authored prose sentence**, in working and final replies. Do not stop after one clue for a whole paragraph or section. A self-contained coloured sentence already supplies a scanning cue; do not duplicate it solely to add an underline. The first underline in a paragraph or section names its concrete subject; later cues can give method, result, quantity or qualification. For example: `The \(\underline{\textsf{export is saved}}\). The \(\underline{\textsf{backup is still pending}}\).` Preserve `not`, `only`, conditions and uncertainty. Do not underline whole sentences mechanically or filler words. Ethan asked to restore the earlier scanning density — 2026-09-23.

Underlines are scanning cues, not status or link markers. Preserve literal quotations, reminders, source text, code, paths, URLs and link labels. Labels/headings/marker-only lines need no underline; important compact table values follow the table scanning rule above, and prose sentences in tables/lists retain useful cues. These rules style assistant replies, not ordinary product UI or documentation. Never emit `<u>` or `</u>` in an assistant reply: Codex can display those tags literally. User correction — 2026-09-23.

## Other-model contributions

User request — 2026-10-04: "at the end of every message if you used a different model only"; "Just tell me quickly what Opus did or what another model did."

User correction — 2026-10-06: "I don't need to see that over and over, just the start and end." For each invocation of a different model, include one short cyan `Models:` sentence when it starts and one when it finishes, including a failed invocation. Do not repeat the same invocation's status during polling, intermediate progress updates or later replies that reuse its result. Its internal model calls and tool turns are not new invocations; a genuinely new invocation gets its own start and end. This supersedes the earlier requirement to include the line on every relevant reply. Name the model and its role. For example: `\(\textsf{\color{#67e8f9}Models: Claude Opus 5.5 reviewed the layout.}\)`. Use ordinary wrapping text or separate short expressions for several models; retain the 64-character limit. No new icon is needed.

Use verified run metadata for the model/version, not an assumed alias; in the start notice, name the requested model and say the version is unverified if metadata has not established it. Distinguish a finished review, implementation, advice, a pending call and a failed call; do not imply that suggestions were accepted or checks executed. Name only the other models whose invocation is starting or finishing in that reply. Omit this line when only the chat's own model worked, including a separate session using that same model or when merely discussing possible models. This formatting rule does not authorize model calls.

In commentary, place the model sentence last. In final replies, place it after the main content and before required environment/outstanding-item footers and the final lavender `About:` reminder, preserving those existing closing rules.

User request — 2026-10-04: At the end of a review invocation's findings, append the Codex/Opus finding split to its completion cyan `Models:` line, in this same colour. Follow [code-review-findings](../code-review-findings/SKILL.md) for verified attribution, deduplication and shared/withdrawn counts; identify the scope being counted. For example: `Models: Claude Opus 5.5 reviewed the change.` followed by `Findings: Codex 2; Opus 3; shared 1.` Split these into short cyan expressions as needed. Findings credit says who identified the issue, not who implemented its fix; do not invent a count when provenance is unavailable.

## Closing reminder and notification

End **only the final reply** with one lavender `#b8a4d9` **About:** reminder. Do not add About reminders to working commentary or progress updates. Split its two short sentences into sans-serif `\(\textsf{\color{#b8a4d9}...}\)` chunks of at most 64 visible characters when needed. Use a concrete overall subject, then useful explanation/action/result/next step. Keep every expression within the 64-character guardrail and leave ordinary spaces between them. No bold, emoji, caret, link, heading or divider in this reminder. It comes after any applicable outstanding-item or environment footer and does not replace the question quote.

Native notifications are a separate optional installation. Read [notification details](references/style-reference.md#notification-summary) when preparing one. Its title always matches the exact current Codex chat name, including its existing emoji; the sender reads it at delivery, never paraphrases it or accepts an agent-authored title. User-requested — 2026-10-02. The body summarizes the whole response with a truthful approved status. No generic “open the task” text. Use the installed preparation helper and measured fit check; never put metadata in the reply or send duplicate manual notifications. If the integration is absent, skip preparation without installing it.

No Env footer in this task or other non-AIMVS work. When giving an outstanding-item recommendation, end the item with its saved explanation in the hover-only `[↗](</Full item explanation>)`; keep the editable Full outstanding items link separate.

## Maintenance and detailed guidance

Preserve and consult the [complete detailed rules](references/style-reference.md) for context/annotation edge cases, notification wording and rendering nuances. They retain the full preference text rather than discarding valid information to shorten this core. Read [verification guidance](references/verification.md) when auditing/testing/changing the skill; it distinguishes code checks from actual rendering and model obedience.

Whenever styling changes, check/update README, website explanations and examples in the same task. Regenerating full-skill HTML alone is insufficient. Validate, regenerate affected demos, commit the intended files and **git push** to the authorised public repository `https://github.com/EthanSK/response-preferences`; verify the remote, deployed assets and installed copy. No renewed routine push approval is needed. Preserve concurrent/unrelated edits and private context; never force-push. Other installers use their own authorised fork/remote.

Publishing Ethan's shared changes is part of making the change: do it in the same task without waiting for a separate sync request. Before reporting completion, compare the installed `SKILL.md`, linked response-rule references, README and changed helpers/examples against the public checkout. Reconcile shareable differences in both directions using the latest explicit preferences; do not blindly copy an older installed file over newer public rules. Publish omitted shareable changes too, preserve genuinely private/local integration settings, and verify the remote commit and affected deployed assets. A local save or an earlier successful deployment is not proof that this update is public. If publication fails, state what remains unpublished. This is an agent's completion step, not a background auto-publisher.

On first use in a task, or the next use after a week, follow [weekly public updates](references/public-updates.md). Keep dates/leases local, check the pinned source, ask before installing an available update, and preserve local edits. Silence is not approval; no daemon or automatic domain actions.
