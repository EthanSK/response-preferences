# Verified project lessons

## Standalone bundling

Use replacement functions when injecting bundled JavaScript into the HTML shell. JavaScript `String.replace` replacement strings interpret `$&`, `$\`` and `$'`; dependency code can contain them. Passing the bundle as a replacement string duplicated HTML fragments and prevented the editor from starting. `scripts/build.mjs` uses literal-returning replacement functions. `tests/editor.test.mjs` boots the actual built template, and the static-site validator checks duplicate IDs.

## Passage mapping

Use markdown-it token source maps, not substring searches. Repeated list entries and nested lists need distinct source locations. Select the smallest mapped passage covering the requested line. Keep frontmatter line numbers intact when presenting it as a compact details block. The cases are covered by `tests/markdown.test.mjs`.

## Editing and saving

CodeMirror's Markdown language needs a `codeLanguages` resolver to colour fenced languages in the source editor. Language-specific support for standalone files alone does not cover fences.

Keep the saved baseline separate from the current editor revision during asynchronous writes. Check the picked file against its previous raw contents before creating a writer, and abort failed writes. Conflict and failure cases are covered by `tests/files.test.mjs`. A browser download is an exported copy, not a saved source; keep the unsaved indicator until a real write or undo restores the baseline.

## Public and private artifacts

The generated HTML includes source text and embedded images. Keep real message context and private viewers outside this repository. Public demos use synthetic text. Validate source round-tripping and script-termination escaping in `tests/test_generator.py`.

## Verification boundaries

User-clicked local HTML and automated local-file access can have different permissions. A tool restriction does not prove the user's link fails. Test public demos through the permitted browser surface; never work around a denied local URL. DOM tests verify behavior but do not establish visual correctness. Inspect actual screenshots for layout and highlight placement.

Use versioned public asset/demo links after updates, then compare live bytes against the commit. Browser extensions can emit errors on sandboxed iframe pages; attribute errors by their source URL before treating them as project failures.

## Search controls

CodeMirror search commits its query on keyup/change; a browser automation fill that only emits input does not exercise normal typing. Verify with real keyboard events. Its stock light button background needs an explicit dark-theme override so labels remain readable. Live keyboard testing confirmed five matches for the sample query.

## Conversation demo panels

Closing a details pane must restore focus to its opener. On small screens the pane covers the conversation, so make the background inert until dismissal. Reopening the same document must preserve its iframe; replacing it needs an explicit reminder to download edits first. These cases are covered by `tests/site.test.mjs`.

## Notification wording and fit

Notification titles describe the user's request in their perspective; a task label or result heading is not interchangeable with that question. Put the status icon with the answer below. Visible macOS text capacity depends on glyph width and available layout, not just character count. Keep the native integration's measured limits separate from public skill wording and push-payload byte limits. The native sender is a separate installation; this repository documents its behavior without bundling it.

## Reply-format regression checks

A saved formatting rule can remain intact while an assistant reply omits it. Validate the actual draft as well as the instructions. The reply-checker tests include the observed plain skill announcement and require magenta serif plus an adjacent existing link. Website tests check CSS variables as well as computed declarations because JSDOM leaves `var(...)` unresolved. Public-demo tests compare embedded source text with current Markdown so updating SKILL.md without regenerating its viewer fails CI. Semantic choice and actual Codex rendering remain separate manual checks.

Nested underline braces inside coloured LaTeX must not bypass palette, font or adjacent-link checks. The old flat-text colour matcher skipped these spans entirely; `tests/test_reply.py` now checks invalid colours/fonts and missing magenta links with nested underlines. This remains a structural check, not a TeX parser or a semantic underline selector.

Reply phase determines marker size: plain commentary markers must pass through the same vocabulary, position, direct-answer and skill-link checks as enlarged final markers. Treating plain commentary as exempt would lose those checks; `tests/test_reply.py` covers both forms and their different caret sizes. The website uses the enclosing assistant message’s `final` class so all working markers, including skill announcements, inherit prose size together.

## Guide controls and responsive state

The macOS traffic lights control only the example window and retain its DOM when closed or minimised, so restoring preserves draft text and the editor. Keep a visible restore route and return focus to the initiating control. Installation prompts copy their visible text; failed clipboard access selects that text for manual copying.

The desktop details card needs a media-query listener to close when moving to a compact viewport, and it closes after a compact-layout navigation choice. CSS alone can otherwise leave the card covering the conversation. Chrome desktop and 390-pixel checks reproduced and verified this transition; `tests/site.test.mjs` covers the state changes.

Copy buttons need explicit foreground and background styles at the same specificity: the general `.copy-row button` rule previously overrode the primary background while leaving its dark text. The installation-button computed-style check preserves the readable pair.

## Inline prose overflow

A long single coloured `\textsf` expression with nested underlines was visibly clipped in Codex desktop 26.901.51231 (8109). The bundled `.katex .base` uses `white-space: nowrap` and inline-block layout. A synthetic reproduction using that client's KaTeX JS/CSS measured 1069px of content in 700px and 316px paragraphs; a short complete coloured statement plus ordinary supporting prose fit both widths. This is an authoring workaround, not an app-renderer fix. The public website uses HTML/CSS and cannot establish native rendering.

The draft checker now rejects inline prose expressions above 80 approximate visible characters, including nested underlines and long topic labels. This catches the observed failure pattern but does not measure glyph widths. Keep spans substantially shorter where possible and preserve negations and qualifications. Literal quotes, code examples and mathematical expressions without prose text commands remain outside this rule.

## Personal desktop wrapper

The desktop menu must reserve the measured widths of the app menus, system controls and clock before choosing visible app icons. A fixed viewport estimate overlapped the clock at 390 pixels; the measured layout was verified in Chrome at mobile and desktop widths. Keep hidden apps reachable through the searchable directory. Escape in that modal must stop propagation so it does not also close an underlying guide pane, and dismissal must restore focus without leaving a stale tooltip.
