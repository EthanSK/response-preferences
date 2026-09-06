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
