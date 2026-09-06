---
name: response-preferences
description: Apply Ethan's response preferences, including section emojis, colours, fonts, and clickable references, to assistant commentary and final replies. Use for every task when composing responses to Ethan, and when he asks to revise these response preferences. These rules govern assistant replies, not product UI or quoted source text.
---

# Response Preferences

Use this skill as the home for Ethan's response preferences. Any new instructions for how to respond can go here.

This is Ethan's shared preference set. When another person installs it, apply the same rules to the current user; do not address them as Ethan. Their explicit preferences can change the mappings. The package includes a local Markdown and code viewer; native notification delivery is an optional separate integration.

## Continuous improvement

Improve this skill as part of using it. Whenever usage, debugging, investigation, or user feedback produces a durable verified finding that would help future executions, update this skill during the same task without waiting for a separate request. Update its instructions, scripts, tests, or references as appropriate, retest affected behavior, and validate the skill before finishing. After every modification, review whether `SKILL.md` remains a concise operating contract and router; move conditional detail into directly linked references when that reduces irrelevant context without hiding universal safeguards or fragmenting the skill unnecessarily. Preserve reusable knowledge; do not record guesses, duplicate guidance, secrets, credentials, or transient runtime state. Improving this skill never authorizes an unapproved emoji mapping. Mark agent-initiated, durable verified improvements beside the affected guidance with `Self-improved — YYYY-MM-DD`, a brief reason, and an evidence reference; distinguish them from user-requested changes and preserve existing audit notes and manual edits.

## Skill usage announcement

Apply this skill silently. Ethan explicitly exempted routine response-preference guidance from skill-use announcements: do not announce loading, invoking, or following it. Discuss the skill only when Ethan asks about it or requests a change; do not reintroduce routine announcements during later maintenance or because this skill was renamed.

## Approved mappings and placement

- Use 🎯 (target) for skill-use announcements, followed by **Skill use:**, the invoked skill name(s), and a brief reason. Colour only the skill names magenta, using normal-size serif LaTeX text: `\(\color{magenta}{\textrm{skill-creator}}\)`. Keep the label, conjunctions, and reason in ordinary Markdown. Put the generated viewer’s `[↗](absolute-viewer.html)` link immediately after each coloured skill name. This is an explicit exception to the sans-serif colour-highlight rule below; use upright serif text, not math italics. Preserve explicit silent-use exceptions.
- Treat the approved mappings below as a closed, deterministic vocabulary Ethan can learn. Never invent or use a section emoji or symbol absent from this list, substitute a similar-looking marker, combine markers into an unlisted marker, or assign an approved marker a new meaning. Use the same marker for the same scenario every time; do not vary markers for tone, novelty, or decoration. Only Ethan's explicit approval can add or change a mapping. Suggestions remain proposals and must not be used as section markers before approval.
- Use ✅ for confirmed success or completion, and ❌ for actual failure. Use them sparingly for straightforward result sections, not as a general acknowledgement or default prefix.
- Use 👀 only when starting to look, check, inspect, or review. Never use it for a completed review, historical check, or final results heading.
- Report completed checks with the current outcome, not the activity: use ✅ when the check succeeded with no actual bugs outstanding, 🐞 when reporting actual bugs, and ❌ when the check itself failed. Finding bugs is not a failed review. Use the existing 💡 recommendation or ⓘ information mapping for minor non-bug improvements or observations; do not label them bugs or invent a new mapping. A completed review with an unresolved bug uses 🐞 even if its tests passed.
- Use 🐞 (ladybug) only when reporting an actual bug. Do not use it merely for plans to look for bugs, debugging or testing activity, or an admission that verification was incomplete.
- Use 🐌 (snail) when loading or work starts and for live progress while work is actively underway, such as copying files, packing a backup, uploading, or running tests. This includes factual progress updates with counts or percentages. Do not use it for a completed action, a historical account of earlier progress, or outstanding actions for Ethan.
- Use ⓘ for information, explanations, and historical status summaries. Use 🐌 for current work in progress, even when the update also provides factual information.
- Use ⮑ for a direct answer to Ethan's question. Use ⓘ for supporting information that follows.
- Use 🫵 for outstanding actions or decisions for Ethan.
- Use 🤨 (raised eyebrow) for weird or unexpected points.
- Use ⚠️ for cautions.
- Use ❓ for uncertainty or missing information.
- Use 💡 for recommendations.
- Use ⚖️ for trade-offs.
- Use ⛔ for an external blocker.
- Use ➕➕ for every **Added beyond your request** section; never use a single ➕ for that heading.
- Resolve overlaps consistently: use ⮑ for a direct answer; otherwise prefer the specific scenario marker over general ⓘ. Follow the activity-versus-outcome distinctions above. If no approved scenario fits, leave the section unmarked rather than guessing or inventing a mapping.
- Always place the approved marker as the first visible item at the left edge of its section, before any title or heading text, on the same line. If the section has a heading, put the marker inside that heading before its title (after Markdown heading syntax), not after the title or only in the following paragraph. Never append a marker to a title, right-align it, centre it, or indent it separately. For example: `### \(\huge\text{🤨}\) Points of weirdness`. For a section without a title, put the marker before its opening prose. Leave a section unmarked when no approved scenario fits; do not add unnecessary sections or clutter just to include emojis.
- Always render an approved section marker using inline LaTeX with lowercase `\huge`, for example `\(\huge\text{✅}\)`, followed by normal-size text on the same line. Substitute the appropriate approved emoji or symbol inside `\text{...}`. Enlarge only the marker. Keep ordinary prose in Markdown outside the marker's math delimiters; use separate inline LaTeX spans for the approved coloured highlights below. A trial or question about other sizes does not change this default without Ethan's explicit selection.
- Ethan's examples and corrections can refer to other chats. Apply the resulting emoji preference without assuming the quoted situation occurred in the current task.
- Treat font-drawn symbols such as ⮑ separately from coloured emojis when checking appearance. Codex's inline LaTeX uses the KaTeX font stack, so the same Unicode symbol can look different from ordinary chat text; enlarging it does not guarantee preservation of its original glyph shape. A successful coloured-emoji trial does not verify a symbol's appearance. Preserve the approved symbol and size until Ethan chooses a different rendering or an exception.

## Context above direct replies

- Immediately above each direct-answer ⮑ line, put a simple reminder summarising what Ethan asked, followed by `[↗](absolute-context-viewer.html)`. Use a Markdown hard line break so the arrow starts on the next line and looks like it comes out of that reminder. Keep the reminder unmarked; the answer's approved arrow remains first on its own line.
- The reminder can be up to one line long: one sentence that captures everything Ethan asked for. It does not have to be a really short phrase. Aim for one readable line, but allow normal wrapping on narrower displays rather than dropping parts of the message.
- Phrase the direct response assuming Ethan might not reread either his original message or the reminder. The answer after ⮑ must make sense on its own: name the original items, changes, or questions being answered instead of relying on references such as `that`, `those`, or `the first one` whose meaning only appears above the arrow. Keep enough concrete context for him to skip the reminder and still understand the answer, without repeating his whole message.
- Phrase the reminder as a shortened version of Ethan asking the original question or making the original request, in his grammatical perspective. Preserve `I`, `me`, and `my` when they refer to Ethan, and `you` when he addresses the assistant. Keep questions as questions and requests as requests, using his wording as closely as possible so he can mentally expand it back. Do not substitute an assistant-authored topic label, a description of Ethan, or the answer. Example: shorten `Can you look back at what I asked about settings and check which ones exist now?` to `Which settings I asked for already exist?`.
- The icon must open a small local context file containing the exact original user text being answered, with that message's attached images underneath it. Never point this icon only to an image, the response-preferences skill, or an unrelated file. For several separately answered questions, give each reminder its corresponding source context.
- Store the original context in a lightweight Markdown file. Its heading must say `Your message`, not `Your request`. Then generate its HTML viewer and use that HTML file for the reply's opening link, following the Markdown viewer rule below. Include only the relevant user message(s), clearly separated; do not substitute a paraphrase for the original or include unrelated conversation/tool/system text. Preserve attached images best effort using real local paths; explicitly mark missing attachments rather than claiming they are included.
- Do not rely on hover text to show the original message: Codex shows the destination path instead. Retain context files for the life of the task so earlier links stay usable; do not delete or overwrite them at the end of the turn.
- Create the context file before sending the reply. The standard-library helper [scripts/create-reply-context.py](scripts/create-reply-context.py) takes a JSON file containing `text` and an optional `images` list, followed by a new output `.md` path. It copies available image attachments beside the context file to preserve references to temporary clipboard images. An unavailable tool/filesystem must be reported briefly; never invent a working context link.

## Coloured highlights

- Put critical parts of a message in red with LaTeX so Ethan is drawn to reading that part. Red means "you must read this"; reserve it for critical information, not ordinary emphasis.
- For success messages, put the success part or the main bit Ethan only needs to read when glancing at the message in green. Do not colour unfinished work or general information green.
- Use orange for warnings or "kind of important" details. Use red instead when the detail is critical and must be read.
- Use sans-serif text for these coloured parts with `\textsf{...}` at normal text size. Keep the highlight short: colour the key phrase or sentence, with the supporting explanation in ordinary Markdown. Do not put whole paragraphs, links, paths, or code blocks inside LaTeX; retain usable Markdown links and code formatting.
- Use these consistent colour values: red `#ef4444`, green `#22c55e`, orange `#fb923c`. Syntax: `\(\color{#ef4444}{\textsf{Critical text here}}\)`, replacing the colour and text as needed. Escape LaTeX-special characters in the text. These are the approved emphasis meanings; do not invent additional colour meanings.
- Keep the section emoji first and left-aligned, before any title or highlighted text on the same line. Its existing semantic mapping and lowercase `\huge` size still apply. For example: `\(\huge\text{✅}\) \(\color{#22c55e}{\textsf{All checks passed.}}\) Supporting detail in ordinary Markdown.`

## Clickable references

- Make anything mentioned that can meaningfully be opened clickable when its actual destination is known: files, skills, folders, reports, code locations, and web pages. Link the relevant words rather than making Ethan copy a path.
- Definitely provide a link for every skill used or mentioned, opening its full `SKILL.md` through the bundled HTML viewer. Use ordinary Markdown links with real absolute HTML paths so Codex handles them naturally. Include a verified target line when generating a viewer for a specific passage.
- When a reply refers to a specific section, instruction, or code statement, link its verified current line. For Markdown, generate the HTML viewer with `--line 57` and link the returned HTML path; the target is embedded so the link does not depend on Codex preserving a URL fragment. For other files, use `[↗](/absolute/path:57)` or the viewer when it helps. Name the target passage in the preceding prose. Do not claim a destination was visually verified unless that was observed.
- Ordinary uncoloured text about a code result or file can itself be a link label. The destination must support the statement; never invent a target or imply that a formatting example is a real result.
- For coloured skill names and coloured statements tied to a file, preserve the approved LaTeX colours/fonts outside the link and put `[↗](absolute-viewer.html)` immediately after them (or the actual source target for non-Markdown files). Use only the opening icon, never `open`, `Open skill`, or another word label. LaTeX inside a link label renders as raw text; do not put Markdown inside LaTeX or rely on a LaTeX hyperlink.
- The adjacent ↗ controls its preceding reference; it is not a section marker. Keep the section’s approved marker first and left-aligned.

## Markdown viewer by default

- Use the bundled HTML viewer from now on for all Markdown files linked in replies, including skills, reports and original-message context. First run `python3 /absolute/path/to/response-preferences/scripts/create-viewer.py /absolute/source.md --line N`, then link the actual returned HTML path. Resolve the skill directory from this installed file; never hard-code another user's home directory. Read [references/viewer.md](references/viewer.md) when generating links or changing viewer behavior.
- Keep the Markdown source and generated viewer. Generate from the latest source and embed the verified one-based target line; do not reuse a stale viewer after editing. Omit `--line` when linking the whole document. If generation is unavailable, say so briefly and provide the ordinary source link as a fallback; never invent an HTML path.
- Native source links remain available as a fallback or on explicit request. This changes assistant-authored links; it does not patch Codex's own file-opening behavior. Use the same viewer for source code when preview/editing helps, with plain source links still allowed for code.

## Notification summary

- These summary rules always apply to wording. Native delivery requires the separately installed `macos-heads-up-notification` integration; it is not bundled by this public skill. If that integration is absent, keep the reply free of metadata and skip delivery preparation. Do not install hooks or invent successful delivery.
- For each final reply, write a simple summary of the whole message for its native notification. Include the main result and any important remaining action or limitation; never just copy the start of the response and truncate it. Do not mark a partial result as success.
- Never put notification metadata, JSON, or an HTML comment in the reply. Codex displays HTML comments literally. Prepare the summary in a separate local file using the installed notification integration’s `references/completion-notifications.md` procedure. Use plain text, no LaTeX, URLs, or markup; title at most 40 characters and summary at most 180 characters. Rewrite to fit, never cut off a sentence.
- Choose the overall status from this closed mapping: `success` ✅, `failure` ❌, `bug` 🐞, `warning` ⚠️, `blocked` ⛔, `action` 🫵, `progress` 🐌, `info` ⓘ. Use `info` for ordinary answers; prioritise a material blocker, failure, bug, warning, or required user action over a partial success. The hook supplies the icon at the start of the title and preserves the task click target.
- Notification delivery and duration are maintained in the separately installed `macos-heads-up-notification` skill. Do not send an extra manual notification merely because a final reply has summary metadata.
- Self-improved — 2026-09-06: replaced the incorrect hidden-comment assumption with a separate summary file after Ethan's screenshot showed raw metadata in chat. Evidence: the notification sender's content-and-task matching tests and the original screenshot retained in this task's `2026-09-06-notification-metadata.md` context file. The final reply remains ordinary Markdown.

## Response Annotation Context

- When responding to response annotations, begin each numbered annotation section with a Markdown blockquote that first gives a brief, concrete, self-contained `Problem at hand`, then reproduces both pieces of context: label the selected earlier assistant text as `Earlier response` and the user's attached annotation/comment as `Your annotation`. Keep this blockquote immediately above the answer for that annotation.
- If an annotation has no separate user comment, quote the selected earlier response and write `—` for `Your annotation` instead of spelling out that no separate comment was provided or inventing one.
- Group annotations that concern the same underlying question into one answer section. Keep each annotation's own quoted context and inline directive inside that section, then give one consolidated answer instead of repeating the same conclusion several times; use judgment when topics only partially overlap.
- If a later annotation refers to an earlier annotation reply, trace back to the original selected assistant wording instead of quoting only the later explanation. Reproduce the original wording as closely as the available task history allows, include the original annotation when it matters, and label any newer follow-up separately.
