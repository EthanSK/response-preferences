# Response Preferences

A personal Codex skill for **how replies are written**. Fixed emoji meanings, coloured highlights, underlined scanning cues, original-message context, and a local Markdown/code editor.

**[Try the website](https://ethansk.github.io/response-preferences/)** · **[Try the editor](https://ethansk.github.io/response-preferences/viewer.html)** · **[Read the skill](SKILL.md)**

Created from Ethan's preferences, shared so you can use or adapt them. The website is an interactive Codex-style conversation demo: three fictional exchanges demonstrate all 17 global markers, colours, underlined sentence clues, quoted question reminders and adjacent opening links. Switch conversations in the sidebar, emphasise a type of reply with the focus controls, or click a marker to read its meaning. File links open an editor pane; its ↗ opens the same document in a full tab. This is a set of agent instructions with helper scripts, not a modification of the Codex app. It cannot guarantee that a model always follows the format.

## What it does

| Feature | Behaviour |
| --- | --- |
| Deterministic markers | Uses a closed vocabulary: the same marker always means the same thing. Only user-approved project mappings may extend it; no arbitrary emoji additions. |
| Meaningful emphasis | Red for critical text, green for confirmed success, orange for warnings, cyan for important information. Every coloured highlight makes sense on its own from its first word, using enough subject and context—even a complete short sentence. Highlight selectively; cyan does not colour a whole information section. |
| Sentence scanning | Underlines the most useful words in every assistant prose sentence, including ordinary and coloured text. Keeps negatives and conditions so scanning does not change the meaning. Exact quotes, code and links remain intact. |
| Computer Use | 🖥️ for manual browser/app interaction, with explicit status wording. Successful manual tests may use green; automated tests and lint remain ordinary text. |
| Project extensions | Additional user-approved mappings apply only in their project; global meanings stay consistent. |
| Context above answers | Uses only the question or excerpt being answered, in your own grammatical perspective, in a blockquote above the direct-answer arrow. |
| Original-message links | Opens a document headed **Your message** with the exact original wording and attached images underneath. |
| Clickable references | Links skills, files and specific passages. Colour stays outside the adjacent ↗ link. |
| Markdown viewer | Generates a self-contained HTML page for Markdown links, with source-line mapping and animated passage highlighting. |
| Code editor | CodeMirror provides syntax highlighting, line numbers, search/replace, undo/redo and bracket matching. Preview, edit and split views. |
| Table grouping | Uses approved markers beside category/status labels when helpful, keeping related rows together. |
| Annotation context | Preserves the full annotation context, then the short question in your wording underneath, then the answer. Groups related answers without dropping either context layer. |
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

When maintaining Ethan’s skill, check the website and README after every response-style change, update affected examples, validate, commit and push to the public repository. Other users should use their own authorised fork.

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
| 🖥️ | Computer Use and manual browser/app tests | | |

Markers stay inline for a single line or short statement. For sections spanning multiple paragraphs or blocks, they sit above the content with a visible ⌄ chevron beside them and apply until the next marker. Start a new marked section when the purpose changes, such as from a successful result to supporting information. Table-cell labels remain inline. The caret points toward the section below; it is a visual cue, not a dropdown control or a new emoji meaning. Write `\(\huge\text{ⓘ}\) \(\LARGE\text{⌄}\)`: keep the emoji at lowercase `\huge` and enlarge the chevron separately to `\LARGE`, one tier above `\Large`. Do not use the old tiny `▾` triangle or mathematical `∨`. Inline and table-cell markers have no caret. Their default rendering is inline LaTeX with lowercase `\huge`; prose stays normal size. ↗ is a link-opening control, not another section marker. Reminders use a blockquote with a vertical line on the left; answers stay outside it. The return arrow stays on the same line as the opening answer, even when a table, list, code block or further paragraph follows. It has no caret. Answers name the actual subjects and make sense even when the reminder is skipped.

Read each highlighted clause or sentence on its own: it should make sense without the uncoloured words before or after it. This applies to all four highlight colours; magenta skill names keep their separate name-only styling.

Highlights use `\textsf{...}` with red `#ef4444`, green `#22c55e`, orange `#fb923c`, or cyan `#67e8f9`. Skill names use upright serif magenta as a deliberate exception. Colours appear outside links because some Codex renderers expose raw LaTeX when it is used as a link label.

Automated test results, lint and other routine automated checks do not get green text. Successful manual tests can use green with 🖥️; failed or incomplete manual tests state that outcome without green. The computer marker takes precedence over generic progress/result markers in Computer Use sections.

Projects can list additional user-approved emoji meanings in their existing instructions. Apply only the relevant project’s mappings; do not invent any or override global meanings without explicit approval. Pass approved extra symbols to the reply checker with repeatable `--approved-project-marker` flags. 🖥️ is global.

## Underlines for scanning

Every assistant prose sentence gets short underlined cues: the subject, action, result or qualification that gives away its meaning at a glance. Read the underlined words in order and keep crucial negatives or limits, such as **not uploaded** or **after restarting**. Avoid underlining filler or whole sentences by default. Exact quotations, code, paths and link labels stay intact; headings and compact labels do not need forced underlines.

Use `The backup was \(\underline{\textsf{not uploaded}}\) because the provider was unavailable.` For colour and underlines together: `\(\color{#67e8f9}{\textsf{The viewer is a \underline{snapshot} of the file.}}\)`. The whole coloured clause still makes sense independently, while its underlined words provide scanning clues. Underlining is not another importance level and does not make text clickable. The website demonstrates it with styled `<u>` spans; ordinary documentation is not formatted as an assistant reply.

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

Notifications lead with a short version of your request, in your wording and perspective. The text below pairs the status icon with a brief answer summary. Titles contain no emoji; the status icon starts the answer below. The native integration measures one title line and two answer lines before accepting the text. There is no universal macOS character count that guarantees a fit. Metadata stays out of chat. This repository does **not** install notification hooks, a native sender, task routing, or display-duration changes. On Ethan's Mac those are provided by a separate `macos-heads-up-notification` integration. Without it, the agent skips notification preparation. All other features work independently.

## Keeping the format consistent

The skill requires a quick check before every reply. Before sending a final reply, save its exact Markdown and run:

```sh
python3 ~/.codex/skills/response-preferences/scripts/check-reply.py /absolute/reply.md
```

This catches missing magenta skill announcements, missing opening links, unknown or misplaced wrapped markers, uppercase `\Huge`, obsolete colour/font combinations, missing question quotes, direct Markdown links and leaked notification comments. It checks local link destinations exist. Quoted earlier messages and code examples are excluded. It does not interpret meaning, guarantee model obedience or verify the app's rendering; see [verification and coverage](references/verification.md).

GitHub Actions runs the test suite on every push and pull request, including regression cases for the reply checker and the website's marker, colour, quote and skill-link presentation.

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

## Weekly update checks

The agent checks the configured public source on first skill use when a week has passed, using a shared local lease to avoid duplicate checks. It can install reviewed, compatible updates and tells you what changed; it preserves local edits and respects opt-outs. No background process is installed. Python 3 is needed for the date/lease helper; the skill can still be used without it. Copied installations need a trustworthy installation baseline; plugin installations use their host updater. See [the update procedure](references/public-updates.md).
