# Live Markdown and code viewer

Read this when linking a file, maintaining the viewer or explaining file access.

## Normal links read the original

Run `python3 <skill-dir>/scripts/create-viewer.py /absolute/document.md --line 45` and link the exact HTTP URL printed. Omit `--line` for the whole document. This uses one shared `index.html` application, not an HTML file generated for each document. Opening the same URL reads the current original file. The header shows its canonical path. Skill metadata is expanded by default. Whole-file links select no passage; only an explicit `--line N`, `#LN` or Go action highlights a passage. A thin yellow line in the existing gutter marks the complete selected passage from start to end, without tinting the text area, flashing or widening the gutter. The code editor marks its target in the existing line-number gutter in both themes. User-requested — 2026-10-17.

The original Markdown/code file is the sole editable document. Clean views check for external changes every 1.5 seconds while visible, and when focused. Unsaved edits remain intact if the disk changes. Save writes the original, preserving BOM/newlines/permissions, and rejects stale revisions. Reload file explicitly discards a draft only after confirmation; Download copy preserves a separate user-requested export.

Preview/Edit/Split, syntax colours, line jumps, search/replace, undo, table resizing and saved Codex appearance reuse existing components. Local referenced text/image files present during registration receive scoped links; new references need another helper invocation. This does not recursively grant a document tree.

## Local file service

`scripts/live-viewer.py` provides the shared app and read/save API at `127.0.0.1:59343`. Python 3.9+ on macOS/Linux is sufficient; the app bundle is included. There are no external uploads, remote scripts or analytics. macOS installs the user LaunchAgent `com.ethansk.codex-live-viewer`; other supported POSIX systems start a detached process. An updated server is restarted by the next helper invocation on macOS. No administrator permission is required.

Registrations live under `$CODEX_HOME/state/live-viewer/` (default `~/.codex/state/live-viewer/`), outside the published skill. Random document capabilities map to explicitly registered canonical paths. The browser cannot register a new arbitrary path. Host/origin checks, save headers, no-store responses and no-referrer policy protect the API. Capability URLs grant local read/write access to their registered file: keep them local and private. Requests and document contents are not logged. Missing files/services produce errors, not embedded stale fallback content.

Atomic replacement and revision checks reject observed concurrent edits. Like ordinary editors, the service cannot provide a filesystem-wide compare-and-swap against another app that ignores locks in the tiny interval before rename; coordinate truly simultaneous writers. Files are UTF-8 text up to 5 MB. Registered PNG/JPEG/GIF/WebP images are limited to 20 MB each. HTML/script execution and remote images remain blocked.

Browsers restrict scripts reading `file://` documents, including neighbouring files in the same directory. A browser file picker is an alternative with a user gesture/permission; the local service supports direct file links without a picker each time. Never weaken browser security flags to work around this boundary.

To stop the macOS service: `launchctl bootout gui/$(id -u)/com.ethansk.codex-live-viewer`. Remove its matching file in `~/Library/LaunchAgents/` to uninstall autostart. Registered source files are untouched. The next normal helper invocation reinstalls the service.

## Explicit snapshots and public examples

Use `--snapshot` for a requested frozen offline artifact. `--output new.html` or `--public --output new.html` also select explicit export. Public mode omits local links/images/appearance; it does not redact source text. Only export already-public or synthetic content to the public repository. Existing old snapshot links remain frozen historical exports; new normal links use the live viewer.

The public website's demo is synthetic and browser-only; it is not connected to a visitor's local service. Pick a file there to use supported browser saving, or download a copy. Public demos are reproducibly rebuilt from their named canonical example files by the build command. They are not additional editable skill sources.

## Installation ownership

For a developer-owned local install, keep one project checkout as the editable source and make the skill installation path a directory symlink to it. Preserve and reconcile existing local edits before replacing a separate installation. Other users can install the published package normally; build artifacts are derived, never edited independently. Private state/configuration stays outside the shared source.

## Maintain and verify

`npm run check` rebuilds the shared app and public examples, then runs tests. Validate the skill, source-line mapping, hostile Markdown, live read/save, stale writes, clean refresh and preserved drafts. Manually test the installed runtime and inspect actual screenshots. Builds do not prove visual correctness. Do not bypass browser automation restrictions.
