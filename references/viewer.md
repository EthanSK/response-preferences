# Markdown and code viewer

Read this when generating a file link, editing the viewer, or explaining its limits.

## Generate a link

The installed template is already built. Only Python 3.9 or later is required:

```sh
python3 /absolute/path/to/response-preferences/scripts/create-viewer.py /absolute/document.md --line 45
```

The command prints a real absolute HTML path. Use `[↗](that-absolute-path)` in the response. The full original document is included, with line 45 highlighted. Omit `--line` for a whole-file reference. Text/code files work too. Generate a new viewer after changing the source; the snapshot does not watch disk changes. No local server is required.

For reply context, first run `scripts/create-reply-context.py` with the original user text and attachments. Then pass the resulting Markdown file to `scripts/create-viewer.py`. The HTML includes supported local images best effort.

Generated files default to `$CODEX_HOME/outputs/viewers/YYYY-MM-DD/` (or `~/.codex/outputs/viewers/`). Their names include a content/template fingerprint and line number. Equivalent invocations reuse the existing file. Keep them for the life of the task. `--output /absolute/new.html` chooses another destination and refuses to overwrite any existing file.

## What the viewer does

- Preview Markdown; edit source; use split view. CodeMirror provides line numbers, search/replace, undo/redo, bracket matching and syntax highlighting.
- Highlight Markdown, JavaScript/TypeScript/JSX, Python, JSON, HTML, CSS, SQL, YAML, shell, Rust and Go. Other UTF-8 text opens as plain text. Fenced Markdown code also has syntax colours.
- Jump to a one-based line using the control or `#L45`. The smallest mapped Markdown passage receives an animated and persistent highlight. Source mode highlights the exact line. Reduced-motion preferences disable the animation.
- Open a different file using the browser picker. Download copy exports edits. Save writes only to a file explicitly opened through the browser's File System Access API, when supported. A generated snapshot never silently gains write access to its original path.
- Warn before leaving/opening another document with unsaved changes. Check the picked file for external edits before saving; refuse a conflicting write and keep the edited copy available. Browsers can suppress unload prompts, so download/save before closing.

## Boundaries

- This is a document editor, not an IDE: no shell, code execution, language server, project search or terminal.
- Browser support controls native save access and file-link opening. If Save is unavailable, use Download copy. Do not claim a download overwrote the source file.
- Saving checks disk contents before writing, but the browser API cannot provide an atomic compare-and-swap against another application writing in the same moment. Save a copy for concurrently edited files.
- Source text is capped at 5 MB. Only UTF-8 text is supported. Local PNG/JPEG/GIF/WebP images are embedded, up to 20 MB each and 40 MB total. Unsupported/missing/remote images show a note. Relative image discovery is best effort; complex Markdown destinations can require simpler paths.
- HTML in Markdown is escaped. Remote images, network requests and script execution from documents are blocked. The generated HTML contains the document and any embedded images: treat it as private if the source is private. Never commit generated private viewers or message context to the public repository.
- Local links inside a document remain best-effort file links; assistant-authored Markdown references must use generated viewers. The helper does not recursively copy a linked document tree.
- `--public` omits local links and images. It does not redact private source text; only use it with already-public or synthetic content.
- A user opening a local HTML link and an automation tool being allowed to open that URL are separate capabilities. Respect tool restrictions; do not describe an automated inspection restriction as proof the user's link is broken.

## Maintain and verify

Run `npm ci`, `npm run check`, then the static-site validator before publishing changes. `npm run build` bundles the editor into `assets/viewer.html`; this generated template is included so recipients need no Node build step. Regenerate public demos after a template change. Test source line mapping, hostile Markdown, text round-tripping, save conflicts and unsaved state. Load screenshots into vision before claiming visual correctness. Never bypass browser automation restrictions to obtain a screenshot.
