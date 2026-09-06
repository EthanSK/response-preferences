# Verification and preference coverage

Read this when changing the skill, auditing prior requests, or testing the response format. The current SKILL.md is the operating contract; this reference defines verification, not another competing set of preferences.

## Before sending

1. Read the current installed skill when beginning a task, and reread it after a response-style correction. Old replies, screenshots and earlier in-memory skill text can contain superseded rules.
2. Check the actual draft. Skill announcements need 🧠, magenta upright-serif names and a separate working ↗ for each name. Apply the response-preferences silent-use exception.
3. Review meaning manually: answer the specific question first, keep the answer understandable without rereading its excerpt, distinguish success from information and live progress, and apply colour selectively to self-contained clauses or sentences. Read every coloured bit from its first word, without its surrounding prose; check it still names the subject and makes sense. Read only the underlined words in each prose sentence in order: check they carry its useful clues and retain crucial negations, uncertainty and conditions. Exact quotations, code and links stay untouched. Keep markers inline for short statements and above sections with multiple paragraphs/blocks, followed by a `⌄` chevron rendered as `\(\raisebox{0.3em}{\Large\text{⌄}}\)`. Keep the return arrow beside the opening answer even when a table, list or code block follows. Tables use ordinary-sized markers and category text.
4. Save final Markdown and run `scripts/check-reply.py /absolute/reply.md`. Fix failures, then prepare notification metadata separately using the installed native integration, if present. If the draft changes afterwards, check and prepare again.

The checker is deliberately limited. It catches common structural regressions in conventional Markdown/LaTeX replies, including the missing-magenta announcement that prompted it. It does not parse every Markdown or LaTeX construct, decide what is important, choose useful underlined words or guarantee sentence coverage, prove a link supports a claim, detect every omitted marker, inspect the Codex renderer, or force another model to obey instructions. A passing result is not a guarantee of perfect formatting.

## Coverage map

| Area | Current contract | Verification |
| --- | --- | --- |
| Vocabulary | Closed 17-marker global list plus user-approved scoped extensions, no inventions; ↗ only opens references | Reply checker; website vocabulary test; meaning review |
| Activity and outcome | 👀 starts inspection, 🐌 live work, ✅ confirmed success, ❌ failure, 🐞 actual bug; other information uses ⓘ | Manual semantic review with activity/outcome cases |
| Other meanings | 🫵 user action, 🤨 unusual, ⚠️ caution, ❓ uncertainty, 💡 recommendation, ⚖️ trade-offs, ⛔ external blocker, 🧠 skill use, ➕➕ extra scope, ⮑ answer | Closed vocabulary and website meaning controls |
| Marker placement | Left aligned, before content; inline for a short statement, standalone with a visible ⌄ chevron for multi-block sections; the return arrow stays beside its opening answer | Reply checker; website structure test; desktop/mobile inspection |
| Marker size | Lowercase `\huge`, only marker enlarged | Checker; website marker size and screenshots |
| Highlighting | Selected self-contained red/green/orange/cyan clauses or sentences in normal-size sans serif; no new colour meanings | Checker; website computed styles; manual reading of each highlight in isolation |
| Computer Use and automated checks | 🖥️ with explicit manual-test status; green only for successful manual tests, never automated tests/lint | Manual semantic check; website example and global/project marker tests |
| Underlined scanning cues | Useful words in every assistant prose sentence, inside colours and ordinary prose; preserve negatives and conditions | Manual sentence-by-sentence clue review; nested-colour checker regression; website quote/link preservation and scanning examples |
| Skill references | 🧠 announcement, each skill name magenta upright serif with a real adjacent ↗; preference skill used silently | Historical failure fixture; local destination check; website computed styles and links |
| Reply context | Relevant question/excerpt, user's perspective, blockquote restored, answer outside it and self-contained | Checker for quote placement; manual perspective/coverage review |
| Original message | Exact source text, heading Your message, images preserved best effort, actual file link | Context helper and image-preservation tests |
| Markdown/code links | Generated HTML by default, specific verified line when relevant, source retained | Generator, parser source maps, target-line and editor tests |
| Viewer | Preview/edit/split, syntax highlighting, search/replace, undo/redo, downloadable copy; explicit picked-file saving only | Viewer tests; browser interaction and screenshots |
| Tables | Approved emoji plus category text, consistent grouping, no decorative new mappings | Website table and manual review |
| Annotations | Full problem/earlier-response/annotation quote, then a separate short question in the user’s perspective, then the answer; required inline directives; related answers grouped | Manual review; quote content excluded from reply lint |
| Notifications | Current separate integration's question/title and status/summary contract; metadata stays out of replies | Reply checker; native integration tests and fit check separately |
| Sharing and maintenance | Public repo and Pages, README/site checked each change, installed/source/remote reconciled, normal push | CI; static validation; generated demo consistency; live bytes and install verification |

## Preference changes and unresolved experiments

Use the latest explicit choice, not every historical experiment simultaneously. The final choices supersede the old smiley/default-tick pattern, original ⏎ glyph, spinner, grey highlight, short whole-message summary, removed quote borders, always-standalone markers, coloured LaTeX inside links and word-labelled opening links. Preserve current notifications rather than restoring their earlier title/body arrangement.

Do not silently adopt unconfirmed experiments. Using a deliberately invalid link destination as a hover-only original message was proposed and sampled, but no successful adoption was confirmed; actual context-file links remain the supported default. This is distinct from the website's own explanatory hover preview.

Native notification banner duration is outside this public package. Doubling it was requested, but no supported measured implementation was established. Do not claim that wording changes or a successful send doubled its duration.

## Maintenance checks

Run `npm run check`, the static-site validator, and skill validation. Regenerate affected public demos. Inspect the changed site in the user's selected browser; test meaningful interactions and both wide/narrow layouts when layout changes. Verify published assets match the committed files and the installed checkout contains the same current skill. CI checks do not block direct Git pushes or Pages deployment by themselves; inspect their result before reporting completion. Never force-push, discard concurrent changes, publish private context, or rewrite old preferences merely to make a test pass.

## Opening answer before a table

The table below does not move the return arrow onto its own line:

```markdown
> How about now?

\(\huge\text{⮑}\) The \(\underline{\textsf{sample copy}}\) \(\underline{\textsf{finished}}\); the upload is \(\underline{\textsf{still waiting}}\).

| Item | Status |
|---|---|
| Sample copy | ✅ Finished |
| Upload | 🫵 Waiting for your destination choice |
```

Use a separate section marker only when the purpose changes. Supporting blocks alone do not require a standalone return arrow.

## Annotation context and short reminder

The full annotation context and short reminder are both required. Keep them as distinct quote blocks, with the answer immediately after the short one:

```markdown
> **Problem at hand:** Keep the short question visible.
> **Earlier response:** The full annotation replaces the short question.
> **Your annotation:** Can I still see my short question below the full annotation?

> Can I still see my short question below the full annotation? [↗](absolute-context-viewer.html)

\(\huge\text{⮑}\) The \(\underline{\textsf{short question}}\) stays \(\underline{\textsf{below the full context}}\), directly above the answer.
```

The opening link must point to the real original-message viewer; the path above is illustrative. Include each real annotation’s required inline directive with its answer. Do not underline or paraphrase the exact earlier-response and annotation quotations.

## Attention finger coverage

Check that working commentary has no attention fingers. The final reply normally has one 🫵 at a real user action or one 👉 before its main self-contained takeaway; two are appropriate only for distinct important items. Quotations and code examples do not count. The checker defaults to final mode; use `--commentary` to reject fingers in work updates. Website checks cover both progress messages and final replies. Review the caret visually: smaller than the emoji and raised toward its vertical centre.

## Context when scanning backwards

Pick a later underlined cue in each paragraph, then read it with the first underline. The first cue should name the concrete topic so the pair makes sense without searching other paragraphs. Use `skill-update decisions` followed by `agent-based`, not an isolated `agent-based`. Re-establish the subject when the topic changes; do not expand every cue into a whole sentence. This is a semantic review, not something the structural checker can prove.
