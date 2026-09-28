# Preventing response-style drift

Instructions do not guarantee model obedience. Keep the core short enough to read completely, read it after compaction/style changes, and retrieve missing ranges if a tool truncates it. The detailed reference retains every earlier rule; it is not another file to concatenate into every initial read.

## Simple authoring and optional diagnostics

Use the short complete expressions in `SKILL.md`: ordinary Markdown prose, one short underline cue when useful, separate self-contained colour highlights, and the fixed About pattern. Do not hand-nest colour and underline or put a paragraph inside LaTeX. The bundled `scripts/check-reply.py` remains a diagnostic for a tricky expression or skill maintenance; it can check explicit math with KaTeX but is not a required step before every reply and cannot guarantee model obedience or client rendering. User-requested simplification — 2026-09-22.

## No automatic repair

Ethan rejected automatic repair: do not install or enable completion guards, hook continuations, daemons or cross-chat wakeups to enforce these preferences. Keep the annotation requirements in the core skill and use the simple complete patterns before sending. Native completion notifications must not request another model turn for formatting or missing metadata. The old guard and exemption helpers are no longer bundled. User correction — 2026-09-20 and 2026-09-22.

Explicit exact-format user instructions take precedence without a hook exception file. A formatting complaint alone is not permission to abandon styling.

## Evidence and checks

Run affected draft-checker and website tests. Test missing and complete annotation context directly, including later clarifications. A passing mechanical check does not prove meaning, visual quality, or perfect model obedience.

## When a checked draft still produces red commands

Compare three distinct artifacts: the draft that passed, the exact final stored by the client, and any subsequent correction. Run the checker on the stored final and diff it against the draft. A passing draft does not cover braces or other text the model adds while emitting the answer. Reuse the validated text unchanged; if it changes, validate again.

Preserve old responses as history. Correct the current requested reply without repeatedly waking tasks or restarting completed domain work. The authoring rules apply before sending; no post-reply repair is installed.
