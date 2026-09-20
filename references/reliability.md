# Preventing response-style drift

Instructions do not guarantee model obedience. Keep the core short enough to read completely, read it after compaction/style changes, and retrieve missing ranges if a tool truncates it. The detailed reference retains every earlier rule; it is not another file to concatenate into every initial read.

## Explicit draft check

Before a final answer, run `scripts/check-reply.py` on the exact draft. Working updates containing LaTeX must use `--commentary` before sending. The checker catches deterministic omissions, marker placement/sizing, colour syntax, skill announcements and excessive inline LaTeX width. It also sends explicit math expressions through bundled KaTeX 0.16.22 with errors enabled, trusted commands disabled and bounded expansion/time. Delimiter mismatches and renderer/runtime failures cannot pass. Node.js must be available on PATH or selected with `RESPONSE_PREFERENCES_NODE`; the copied bundle has no npm/runtime network dependency. Meaning, per-sentence underline quality, useful emphasis and native visual rendering still require judgment. Single-dollar syntax is intentionally excluded to avoid interpreting prices as math; use explicit delimiters for authored math.

## No automatic repair

Ethan rejected automatic repair: do not install or enable completion guards, hook continuations, daemons or cross-chat wakeups to enforce these preferences. Keep the annotation requirements in the core skill and validate the exact draft before sending. Native completion notifications must not request another model turn for formatting or missing metadata. Legacy guard helpers are not an installation instruction and must not be wired into the completion hook. User correction — 2026-09-20.

Explicit exact-format user instructions take precedence without a hook exception file. A formatting complaint alone is not permission to abandon styling.

## Evidence and checks

Run affected draft-checker and website tests. Test missing and complete annotation context directly, including later clarifications. A passing mechanical check does not prove meaning, visual quality, or perfect model obedience.

## When a checked draft still produces red commands

Compare three distinct artifacts: the draft that passed, the exact final stored by the client, and any subsequent correction. Run the checker on the stored final and diff it against the draft. A passing draft does not cover braces or other text the model adds while emitting the answer. Reuse the validated text unchanged; if it changes, validate again.

Preserve old responses as history. Correct the current requested reply without repeatedly waking tasks or restarting completed domain work. The rules and draft check apply before sending; no post-reply repair is installed.
