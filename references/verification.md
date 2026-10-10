# Verification and preference coverage

Read this when changing the skill, auditing prior requests, or testing the response format. The current SKILL.md is the operating contract; this reference defines verification, not another competing set of preferences.

## Before sending

0. Compare every distinct meaningful question in the complete authored request and earlier unanswered follow-ups with the actual final draft. Check a multi-question request followed by a small correction or status question: older unanswered questions still need an explicit answer, verified action or stated unknown/blocker. Check a claim that a question was missed against the original message and actual prior reply: if it was answered, correct the account and answer clearly again; if the prior reply is unavailable, report that uncertainty rather than infer omission. This is a semantic check, not proof a structural checker can supply or a guarantee of future model obedience. User-requested — 2026-10-10.
   Related questions may share one answer, but list every distinct ask and map each to that answer. Verify the closing coverage line underneath About against the actual draft, including the number of contributing user messages and carried-over questions; repeated selections/wording do not add questions. Test three asks across two messages, one from the earlier message: a shared answer to two and an explicit unknown for the third means three replies, not three completed tasks. An update saying only “I will check” means zero replies, not three. Only final replies have the closing pair and say `this final draft`. Verify that working commentary, progress updates and skill announcements contain neither About nor Questions counts, while internal question tracking continues. User-requested — 2026-10-10.
1. Read the current installed core at task start, after compaction or a response-style correction, at least every five assistant messages (commentary included), and immediately before each final reply. Before presenting or restating review findings, reread the installed global and applicable project review contracts too. Old replies, screenshots and earlier in-memory skill text can contain superseded rules.
2. Check the actual draft. Skill announcements need 🧠, magenta upright-serif names and a separate working ↗ for each name. Apply the response-preferences silent-use exception.
3. Review meaning manually: answer the specific question first, keep the answer understandable without rereading its excerpt, distinguish success from information and live progress, and apply colour selectively to self-contained clauses or sentences. Read every coloured bit from its first word, without its surrounding prose; check it still names the subject and makes sense. Check important bold wording has an underline on the same words, including opening answers and list lead-ins; bold alone does not satisfy scanning. In working and final prose, read only the underlined clues in order: check they retain crucial negations, uncertainty and conditions. Working commentary uses normal-size markers. Exact quotations, code and links stay untouched. Keep markers inline for short statements and above sections with multiple paragraphs/blocks, followed by a `⌄` chevron. Final replies use lowercase `\huge` with the caret rendered as `\(\raisebox{0.3em}{\Large\text{⌄}}\)`. Keep the return arrow beside the opening answer even when a table, list or code block follows. Tables use ordinary-sized markers and category text.
4. Use the complete short patterns in the core skill. Check each opening `\(` has its closing `\)`; `}}` closes the underline commands, not the expression. User correction — 2026-10-05. For a tricky expression or skill maintenance, `scripts/check-reply.py /absolute/reply.md` is an optional syntax diagnostic. It does not need to run for every outgoing reply. Prior check results never prove a new reply is correct. User-requested simplification — 2026-09-22.

The checker is deliberately limited. It catches common structural regressions in conventional Markdown/LaTeX replies, including the missing-magenta announcement that prompted it. It does not parse every Markdown or LaTeX construct, decide what is important, choose useful underlined words or guarantee sentence coverage, prove a link supports a claim, detect every omitted marker, inspect the Codex renderer, or force another model to obey instructions. A passing result is not a guarantee of perfect formatting.

Use `--require-question-coverage` during a coverage-format diagnostic. It requires the line only in final replies and checks its structure, arithmetic bounds, final wording and placement under About; commentary rejects both footers even without that opt-in flag. It it cannot infer the real questions or certify that Y answers exist. Keep legacy snippets usable without that opt-in flag. No automatic reply hook is added.

## Coverage map

| Area | Current contract | Verification |
| --- | --- | --- |
| Vocabulary | Closed 20-marker global list plus user-approved scoped extensions, no inventions; ↗ only opens references | Reply checker; website vocabulary test; meaning review |
| Activity and outcome | 👀 starts inspection, 🐌 live work, ✅ confirmed success, ❌ failure, 🐞 actual bug; other information uses ⓘ | Manual semantic review with activity/outcome cases |
| Tests | 🧪 marks test information, progress and results with explicit status; 🖥️ remains Computer Use and 🐞 actual bugs; automated results stay uncoloured | Reply checker in both phases; home/export examples, test popover and filter |
| Planning and brainstorming | 🛠️ is one shared category for options, approaches and next steps; ⓘ remains facts and 🐌 execution underway | Reply checker in both phases; home example, click popover and planning filter |
| Other meanings | 🫵 user action, 🤨 unusual, ⚠️ caution, ❓ uncertainty, 💡 recommendation, ⚖️ trade-offs, ⛔ external blocker, 🧠 skill use, ➕➕❗ extra scope, ⮑ answer | Closed vocabulary and website meaning controls |
| Marker placement | Left aligned, before content; inline for a short statement, standalone with a visible ⌄ chevron for multi-block sections; the return arrow stays beside its opening answer | Reply checker; website structure test; desktop/mobile inspection |
| Marker size | Plain normal-size markers in commentary, including 🧠, except an enlarged ⮑ direct answer; lowercase `\huge` in final replies; normal-size table labels | Phase-specific checker fixtures; website marker size and screenshots |
| Highlighting | Selected self-contained red/green/orange/cyan clauses or sentences in normal-size text; no new colour meanings | Checker; website computed styles; manual reading of each highlight in isolation |
| Computer Use and automated checks | 🖥️ with explicit manual-test status; green only for successful manual tests, never automated tests/lint | Manual semantic check; website example and global/project marker tests |
| Underlined scanning cues | Prefer a short cue in working and final prose sentences; self-contained colour can carry the cue; preserve negatives and conditions | Manual sentence-by-sentence clue review; website quote/link preservation and scanning examples |
| Skill references | 🧠 announcement, each skill name magenta upright serif with a real adjacent ↗; preference skill used silently | Historical failure fixture; local destination check; website computed styles and links |
| Reply context | Relevant question/excerpt in selectable chunks of at most 64 visible characters, with a repeating 24-colour per-word rainbow, user's perspective, answer outside it and self-contained | Quote helper validates its authored KaTeX directly; general checker still excludes evidence; manual wording and width review |
| Original message | Exact source text, heading Your message, images preserved best effort, actual file link | Context helper and image-preservation tests |
| Markdown/code links | Generated HTML by default, specific verified line when relevant, source retained | Generator, parser source maps, target-line and editor tests |
| Viewer | Preview/edit/split, syntax highlighting, search/replace, undo/redo, downloadable copy; explicit picked-file saving only | Viewer tests; browser interaction and screenshots |
| Tables | Approved emoji plus category text, consistent grouping, no decorative new mappings | Website table and manual review |
| Annotations | Full problem/earlier-response/annotation quote, then a separate short question in the user’s perspective, then the answer; required inline directives; related answers grouped | Manual review; quote content excluded from reply lint |
| Notifications | Current separate integration's live exact-chat-title and status/summary contract; metadata stays out of replies | Reply checker; native integration tests and fit check separately |
| Other-model contributions | Short cyan Models line once at each other-model invocation's start and end; no repeated polling/progress/reuse notices; verified model and role; omitted for chat-only work; before required final footers/About | Semantic check against actual run metadata: one invocation across several progress messages gets two notices, a new invocation gets its own pair, and chat-only work gets none; format demonstration and rendered sample |
| Sharing and maintenance | Public repo and Pages, README/site checked each change, installed/source/remote reconciled, normal push | CI; static validation; generated demo consistency; live bytes and install verification |

## Preference changes and unresolved experiments

### Formatting complaints are not exceptions

Self-improved — 2026-09-09: a formatting complaint was incorrectly interpreted as a plain-text request. Check this semantic boundary before using the exact-format helper: “Why is the formatting broken?” requires repairing the styled reply and checking it; “Reply in plain text without LaTeX” explicitly permits an exception. The checker cannot infer user intent, so a quoted complaint alone is not evidence of approval.

Use the latest explicit choice, not every historical experiment simultaneously. The final choices supersede the old smiley/default-tick pattern, original ⏎ glyph, spinner, grey highlight, short whole-message summary, removed quote borders, always-standalone markers, coloured LaTeX inside links and word-labelled opening links. Preserve current notifications rather than restoring their earlier title/body arrangement.

Ethan confirmed and adopted the original-text-as-destination hover control on 2026-09-07. A short single-line question appeared in the native Codex popup with a leading slash. This is a hover-only exception, not a working file link. Keep real context viewers for attachments and clickable context. Long text, line breaks and special characters remain unverified; distinguish these limits from the successful short-text trial. The website preview is a simulation, not evidence of native rendering.

Native notification banner duration is outside this public package. Doubling it was requested, but no supported measured implementation was established. Do not claim that wording changes or a successful send doubled its duration.

## Maintenance checks

Run `npm run check`, the static-site validator, and skill validation. Regenerate affected public demos. Inspect the changed site in the user's selected browser; test meaningful interactions and both wide/narrow layouts when layout changes. Verify published assets match the committed files and the installed checkout contains the same current skill. CI checks do not block direct Git pushes or Pages deployment by themselves; inspect their result before reporting completion. Never force-push, discard concurrent changes, publish private context, or rewrite old preferences merely to make a test pass.

## Opening answer before a table

The table below does not move the return arrow onto its own line:

```markdown
> How about now?

\(\huge\text{⮑}\) The **sample copy finished**; the upload is **still waiting**.

| Item | Status |
|---|---|
| Sample copy | ✅ Finished |
| Upload | 🫵 Waiting for your destination choice |
```

Use a separate section marker only when the purpose changes. Supporting blocks alone do not require a standalone return arrow.

## Annotation context and short reminder

Repeat the context-and-rainbow check in a read-only side conversation with an Agent Flow full prompt: retain the applicable three context fields and a separate rainbow reminder based on its authored words immediately above ⮑, minimally clarifying the resolved subject when needed. Run the documented standard-input helper with an explicit offset and verify the shared counter remains unchanged; source tracing and formatting must not mutate the main workspace. User correction — 2026-09-30.

The full annotation context and short reminder are both required. Separate distinct annotation-response sections with `---`, including Agent Flow selections, while keeping each section's context, short question and answer together. Verify the two-answer divider in the website demo. Keep context and reminder as distinct quote blocks, with the answer immediately after the short one:

```markdown
> **Problem at hand:** Keep the short question visible.
> **Earlier response:** The full annotation replaces the short question.
> **Your annotation:** Can I still see my short question below the full annotation?

> Can I still see my short question below the full annotation? [↗](absolute-context-viewer.html)

\(\huge\text{⮑}\) The **short question stays below the full context**, directly above the answer.
```

For an Agent Flow code selection `if (count <= 100) return smallWorker;` followed by “Why this limit?”, verify that the response keeps all three fields: `Problem at hand` names worker selection, `Earlier response` quotes the code and identifies its app/file source, and `Your annotation` quotes “Why this limit?”. Repeat with coloured/escaped `app_selection` text and without a native annotation directive. The short rainbow reminder alone fails this check. An unrelated reading highlight and an ordinary standalone question must not acquire invented annotations. This is a manual semantic check; a structural checker cannot infer the omitted source context. User-requested hardening — 2026-09-27.

For that Agent Flow case, run `scripts/check-reply.py /absolute/reply.md --require-annotation-context`: the explicit flag requires all three nonempty fields before the first direct answer even without native annotation references. Check that a rainbow-only draft, each missing or empty field, and context placed after the answer fail; the complete draft passes. The flag diagnoses this supplied context requirement, not whether an arbitrary selection is relevant. It remains optional and does not install automatic repair or a message-counting hook. User request — 2026-10-03.

The opening link must point to the real original-message viewer; the path above is illustrative. Include each real annotation’s required inline directive with its answer. Do not underline or paraphrase the exact earlier-response and annotation quotations.

## Attention finger coverage

Check that working commentary has no attention fingers. The final reply normally has one 🫵 at a real user action or one 👉 before its main self-contained takeaway; two are appropriate only for distinct important items. Quotations and code examples do not count. The checker defaults to final mode; use `--commentary` to require normal-size markers, an enlarged ⮑ direct answer and no fingers in work updates. Website checks cover both progress messages and final replies. Review the caret visually: smaller than the emoji and raised toward its vertical centre.

## Context when scanning backwards

Read each rainbow reminder without the answer or context block. For “if it's like a one-time thing” about pausing hidden components, check that the reminder names the resolved subject, such as “Can we pause the whole hidden component at once?”. For a self-contained “Can you pause hidden Comments refreshes?”, keep the wording; when the subject is genuinely ambiguous, preserve more relevant context instead of guessing. Keep questions/requests in Ethan's perspective, the exact annotation/source quotes unchanged, and the existing 80-character maximum. These are manual semantic checks; syntax validation cannot resolve a pronoun. User request — 2026-10-04.

Read each annotation answer without the later sections. A term such as “attached” must be explained at its first mention: “The panel stays attached — Angular can still update it while it is hidden.” Include the relevant limitation there too, such as ordinary subscriptions needing their own pause. “More clarification below” may introduce extra detail, but must not postpone an explanation needed to understand the first answer. Repeat this check for ordinary and side chat replies. This is a manual semantic check; syntax tests cannot prove the explanation is complete. User request — 2026-10-04.

In working and final prose, pick a later underlined cue in each paragraph, then read it with the first cue. The first should name the concrete topic so the pair makes sense without searching other paragraphs. Use `skill-update decisions` followed by `agent-based`, not an isolated `agent-based`. Re-establish the subject when the topic changes; do not expand every cue into a whole sentence. This is a semantic review, not something the structural checker can prove.

## Inline prose overflow

A long single coloured `\textsf` expression with nested underlines was visibly clipped in Codex desktop 26.901.51231 (8109). The bundled `.katex .base` uses `white-space: nowrap` and inline-block layout. A synthetic reproduction using that client's KaTeX JS/CSS measured 1069px of content in 700px and 316px paragraphs; a short complete coloured statement plus ordinary supporting prose fit both widths. This is an authoring workaround, not an app-renderer fix. The public website uses HTML/CSS and cannot establish native rendering.

Ordinary Markdown surrounds short complete style expressions. The optional checker rejects styled chunks above 64 approximate visible characters and malformed LaTeX. It does not measure glyph widths. Links, code, paths, literal quotes and mathematical expressions without prose text commands remain explicit exceptions.

## Viewer link existence

Self-improved — 2026-10-04: a skill announcement linked a guessed fingerprint path that did not exist. Regenerating the viewer returned an existing file. Copy the helper’s exact output and check `Path(returned_path).is_file()` before posting; this verifies link existence, not document accuracy or browser permission. A nonexistent synthetic path must fail the same check.

## Prices in styled prose

Self-improved — 2026-10-09: an unescaped dollar sign in a fully closed underline produced red raw commands. `test_prices_render_with_currency_in_plain_and_styled_text` verifies that the existing KaTeX diagnostic rejects `\(\underline{\textsf{Pro $500 upgrade grants access}}\)` and accepts both `\$500` inside the cue and `$500/month` outside it. Closing-delimiter checks alone cannot catch this separate authoring error. Reading the rule or testing an older reply does not validate the current draft; the checker stays optional and cannot force model obedience.

User correction — 2026-10-09: dollar signs and prices are allowed; the agent handles their formatting. The same renderer test covers literal dollar prices in ordinary Markdown and escaped dollar prices in underlines, colours and About reminders, including decimal and comma-separated amounts. This verifies valid syntax, not future model compliance.

## Literal symbols in styled prose

User-requested hardening — 2026-10-09: keep ordinary symbols usable and visible, especially percentages, without prohibiting them or changing their values. `test_percent_cues_preserve_the_complete_visible_text` rejects both fully delimited bare-percent failures and accepts their escaped forms. `test_styled_literal_symbols_preserve_visible_text` checks underlines, colour and About text with percentages, dollars, hashes, underscores, ampersands, literal braces, tildes, carets and backslashes. It compares the renderer's visible text with the original literal text, rather than only checking for a successful parse; real mathematical subscripts and colour arguments stay covered separately. The core, detailed guidance, README and website examples use the same allowed-symbol rule. Renderer tests prove syntax and preserved visible text, not that every future model will follow the instructions or that native Codex has rendered a future reply correctly.

## Colour declaration and closing braces

User-requested clarification — 2026-10-09: a coloured percentage in the fourth row of an emitted table had one extra closing brace: `\(\textsf{\color{#67e8f9}100\%}}\)`. Its corrected form is `\(\textsf{\color{#67e8f9}100\%}\)`. The percent was already escaped and the colour-code hashtag was valid. The source session's last skill read contained both the existing one-brace colour ending and the allowed-symbol guidance, with no truncation notice; no draft-check invocation was logged before that final. This is an authoring error despite available instructions, not evidence of missing symbol support or a parser accepting the fault. The trace does not establish the model's internal reason for adding the brace.

`test_compact_colour_and_underline_values_have_distinct_endings` verifies accepted colour and underline forms preserve the visible `100%`, and that the extra brace is rejected. `test_extra_closing_brace_in_fourth_table_row_is_rejected` passes the complete synthetic four-row Markdown table through the reply checker, verifies the row's KaTeX error, and verifies its corrected table passes. The existing renderer already detected the malformed cell; its implementation is unchanged. The instructions now explain the group boundary beside a complete compact-value example. These checks prove the repaired syntax and diagnostic coverage, not future model compliance or native Codex appearance. No mandatory per-message check, automatic repair hook or continuation was added.
