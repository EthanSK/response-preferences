# Response Preferences

A personal Codex skill for **how replies are written**. Fixed emoji meanings, coloured key text, original-message context, and a local Markdown/code editor.

**[Try the website](https://ethansk.github.io/response-preferences/)** · **[Try the editor](https://ethansk.github.io/response-preferences/viewer.html)** · **[Read the skill](SKILL.md)**

Created from Ethan's preferences, shared so you can use or adapt them. The website demonstrates the same dark response layout, markers, colours, context reminders and adjacent opening links. This is a set of agent instructions with helper scripts, not a modification of the Codex app. It cannot guarantee that a model always follows the format.

## What it does

| Feature | Behaviour |
| --- | --- |
| Deterministic markers | Uses a closed vocabulary: the same marker always means the same thing. No arbitrary emoji additions. |
| Meaningful emphasis | Red for critical text, green for confirmed success, orange for warnings, cyan for important information. Only key phrases are coloured. |
| Context above answers | Summarises your message in your own grammatical perspective, immediately above the direct-answer arrow. |
| Original-message links | Opens a document headed **Your message** with the exact original wording and attached images underneath. |
| Clickable references | Links skills, files and specific passages. Colour stays outside the adjacent ↗ link. |
| Markdown viewer | Generates a self-contained HTML page for Markdown links, with source-line mapping and animated passage highlighting. |
| Code editor | CodeMirror provides syntax highlighting, line numbers, search/replace, undo/redo and bracket matching. Preview, edit and split views. |
| Annotation context | Preserves the selected earlier response and your annotation, grouping related answers. |
| Notification wording | Defines short, complete notification summaries. Native notification delivery is an optional **separate** integration. |

The response-preference skill itself is used silently. Other skill announcements use 🎯 with a magenta skill name and an adjacent opening link.

## Install

Requirements: Codex with local skills support and **Python 3.9+** for generated viewers and message-context files. The built viewer is included; no Node installation or build step is needed to use it.

```sh
git clone https://github.com/EthanSK/response-preferences.git ~/.codex/skills/response-preferences
```

Use your configured Codex home instead of `~/.codex` if different. If that destination already exists, preserve it and compare your changes before installing; the clone command deliberately fails rather than replacing it.

Add this instruction to your global or project `AGENTS.md`:

```text
Use $response-preferences for all replies.
```

You can also invoke `$response-preferences` explicitly. Start a fresh task if an already-running task retains earlier instructions. The formatting defaults follow Ethan's choices; edit `SKILL.md` to change them for yourself. LaTeX appearance and file links depend on the chat client's renderer.

For updates, use `git pull --ff-only` only after reviewing your local edits. Keep personal overrides on your own branch or fork. Do not discard customised preferences to update.

## Marker vocabulary

| Marker | Meaning | Marker | Meaning |
| --- | --- | --- | --- |
| ⮑ | Direct answer | ⓘ | Information |
| ✅ | Confirmed success | ❌ | Failure |
| 👀 | Starting an inspection | 🐌 | Work actively in progress |
| 🐞 | An actual bug | 🫵 | Your action or decision |
| 🤨 | Unexpected behaviour | ⚠️ | Caution |
| ❓ | Missing information | 💡 | Recommendation |
| ⚖️ | Trade-offs | ⛔ | External blocker |
| 🎯 | Skill use | ➕➕ | Added beyond your request |

Markers stay inline for a single line or short statement. For sections spanning multiple paragraphs or blocks, they sit alone above the content and apply until the next marker. Start a new marked section when the purpose changes, such as from a successful result to supporting information. Table-cell labels remain inline. Their default rendering is inline LaTeX with lowercase `\huge`; prose stays normal size. ↗ is a link-opening control, not another section marker.

Highlights use `\textsf{...}` with red `#ef4444`, green `#22c55e`, orange `#fb923c`, or cyan `#67e8f9`. Skill names use upright serif magenta as a deliberate exception. Colours appear outside links because some Codex renderers expose raw LaTeX when it is used as a link label.

## Generate a viewer

```sh
python3 ~/.codex/skills/response-preferences/scripts/create-viewer.py /absolute/path/to/document.md --line 45
```

The command prints the generated HTML path. Link that file in a reply using an absolute Markdown file link. The requested line is embedded into the page; `#L45` also works inside browsers. The same command accepts source code and other UTF-8 text files.

Use `--output /absolute/new-viewer.html` for an explicit destination. Existing explicit outputs are never overwritten. Default outputs are cached by content/template/line under `~/.codex/outputs/viewers/` (or `$CODEX_HOME/outputs/viewers/`). Regenerate after changing the source. The page is a snapshot, not a live file watcher.

For original-message context, create JSON containing `text` and optional `images` (absolute paths), then run:

```sh
python3 scripts/create-reply-context.py /absolute/message.json /absolute/new-context.md
python3 scripts/create-viewer.py /absolute/new-context.md
```

The context helper preserves exact message text and copies available attachments so temporary clipboard paths can expire without breaking earlier links. Keep context and generated viewers for the task's lifetime.

## Editing and privacy

- **Download copy** exports the edited source. It does not overwrite the original.
- **Open file** lets you choose a file on disk. Browsers supporting the File System Access API can then enable **Save** for that picked file. Otherwise, download the copy.
- Saving checks for external edits first and refuses a conflicting write. This is not an atomic lock against other applications; use a copy for files being edited concurrently.
- Unsaved edits get an indicator and navigation warning. Browser policies can suppress unload prompts; save or download before closing.
- Files remain in the browser. The viewer has no server, analytics, remote scripts or upload endpoint. Markdown HTML is escaped, and remote images do not load.
- A generated HTML file **contains its document text and any embedded images**. Keep it private when its source is private. `--public` removes local image/link embeddings; it does not redact the source text.
- Text is limited to 5 MB. PNG/JPEG/GIF/WebP images can be embedded up to 20 MB each, 40 MB total. Complex image destinations and local links are best effort. Linked Markdown trees are not recursively copied.
- The editor highlights Markdown, JavaScript/TypeScript/JSX, Python, JSON, HTML, CSS, SQL, YAML, shell, Rust and Go. Other text opens without language-specific highlighting. There is no code execution, terminal or language server.

See [viewer instructions](references/viewer.md) for details. User clicks and automated browser access have separate permissions: an automation restriction does not mean a local link is broken.

## Optional notifications

The skill specifies concise titles, whole-reply summaries and status icons, without putting hidden JSON or HTML comments into chat. This repository does **not** install notification hooks, a native sender, task routing, or display-duration changes. On Ethan's Mac those are provided by a separate `macos-heads-up-notification` integration. Without it, the agent skips notification preparation. All other features work independently.

## Develop

Node.js 22+ and Python 3.9+:

```sh
npm ci
npm run check
```

`src/` holds the editor, styles and HTML shell. `npm run build` produces the self-contained `assets/viewer.html` template. Tests cover source preservation, Markdown line mapping, active-content rejection, generator boundaries, and editor interaction/state.

The simple public site is in `docs/`, served by GitHub Pages from `main:/docs`. Rebuild public demos with `python3 scripts/build-demos.py` after changing the skill or viewer. Public examples are synthetic; never add actual conversations, clipboard images, home-directory paths or generated private viewers to this repo.

## Licence and dependencies

MIT. CodeMirror, markdown-it, Highlight.js and their dependencies retain their own MIT licences. The included bundle contains third-party code; see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md). This project is independent of OpenAI and is not an official Codex feature.
