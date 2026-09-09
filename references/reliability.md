# Preventing response-style drift

Instructions do not guarantee model obedience. Keep the core short enough to read completely, read it after compaction/style changes, and retrieve missing ranges if a tool truncates it. The detailed reference retains every earlier rule; it is not another file to concatenate into every initial read.

## Explicit draft check

Before a final answer, run `scripts/check-reply.py` on the exact draft. Working updates containing LaTeX must use `--commentary` before sending. The checker catches deterministic omissions, marker placement/sizing, colour syntax, skill announcements and excessive inline LaTeX width. It also sends explicit math expressions through bundled KaTeX 0.16.22 with errors enabled, trusted commands disabled and bounded expansion/time. Delimiter mismatches and renderer/runtime failures cannot pass. Node.js must be available on PATH or selected with `RESPONSE_PREFERENCES_NODE`; the copied bundle has no npm/runtime network dependency. Meaning, per-sentence underline quality, useful emphasis and native visual rendering still require judgment. Single-dollar syntax is intentionally excluded to avoid interpreting prices as math; use explicit delimiters for authored math.

## Optional automatic completion guard

`scripts/guard-reply.py` exposes `errors_for(last_assistant_message)` and `repair_context(errors, skill_dir)` for a supported local completion-hook adapter. A JSON stdin invocation is also available for inspection; its output contains errors and, on the first failed pass, a formatting-only continuation request. This package does **not** install global hooks automatically for other users.

The guard checks the actual final reply even if its author skipped the explicit draft checker. It normalizes the trailing memory-citation transport, catches entirely missing prose underlines, and leaves empty, JSON-only, code-only and quote-only outputs alone. It does not read arbitrary transcripts, send messages, access the network, or write state.

Use a trusted, synchronous Stop adapter. Keep the existing user-task/side-task routing. Run the guard only on user-facing finals; do not impose user-facing prose on internal subagent output. For a failed first pass, request one correction to the original answer and matching notification preparation, preserving the completed work. On `stop_hook_active`, report remaining errors without another continuation. Do not add an independent retrying hook beside a retrying notification hook: combine their feedback so they share one bounded repair. Explicit user format requirements override style defaults. A local adapter should provide an off switch.

The conservative automatic check does not enforce project-specific vocabulary or local-file/hover destinations because those need task context. It cannot prove correct cyan/green meaning, cover commentary before it streams, hide an already displayed bad reply, guarantee a successful correction, or affect another client/machine without that adapter. Its success is evidence of a checked final, not perfect compliance.

### Explicit exact-format requests

The guard sees the reply, not the user's request. For an explicit request such as “reply with only this text” or “return YAML only”, prepare a local exception before the final reply. Run `python3 <skill-dir>/scripts/exempt-reply.py <payload.json>` with `reply_file` (the exact draft's absolute path), `session_id` (the originating task UUID), `reason: "explicit_user_format"`, and `request` (the user's actual format instruction). The adapter must call `is_exempt(home, session_id, reply)` before checking style. This does not exempt notification preparation.

The helper stores a private record under the Codex home, keyed by task UUID and the SHA-256 of the reply. Different text or another task does not inherit the exception. Quote the real instruction; never manufacture one to bypass the check. The agent remains responsible for deciding if the request conflicts with styling. If it forgets to prepare the exception, the single repair can prepare it without decorating the answer; an unnecessary continuation is still possible. This is a bounded fallback, not an automatic understanding of every user format.

Ethan's completion-notification adapter can opt in through the local `~/.codex/hooks/response-style-guard.enabled` marker file. Deleting that file disables only this style guard, without changing notification delivery or the skill. It checks routed `Stop` replies only; `SubagentStop` does not prove a user-facing side chat and keeps its existing notification path without style enforcement. The adapter records `style_repair_required` or `style_repair_exhausted` using its existing local receipt mechanism. After an exhausted correction, remaining cosmetic errors do not suppress an otherwise valid exact-reply notification. It runs against the installed skill on the next hook invocation; an old session using asynchronous completion hooks cannot be made synchronous by changing the script alone.

## Evidence and checks

The initial food-clarification reply loaded 11,814 tokens through a 5,000-token tool-output limit, omitted required styling and skipped the checker. Its plain skill announcement and missing final finger/underlines are representative regression fixtures, with private user wording excluded from this public repository.

Run the guard tests, existing checker tests, generator round-trip checks and website checks. Test first failure, valid correction, failed correction without looping, empty/structured replies and unchanged notification routing. Validate an actual installed hook invocation separately from pure unit tests. An agent can still ignore a continuation, so report that boundary honestly.

## When a checked draft still produces red commands

Compare three distinct artifacts: the draft that passed, the exact final stored by the client, and any subsequent correction. Run the checker on the stored final and diff it against the draft. A passing draft does not cover braces or other text the model adds while emitting the answer. Reuse the validated text unchanged; if it changes, validate again.

A local `style_repair_required` receipt proves the adapter detected an error and reached its request branch. It does not prove the client accepted the output, started a continuation, or displayed a valid correction. Inspect actual task history for that correction, check hook exit/output and synchronous configuration, and check whether another Stop hook returned `continue: false`. If no correction appears, report the continuation failure independently from the model's malformed output; do not call the parser ineffective when it rejected the actual final.

Preserve the old response as historical evidence. When authorized, request one formatting-only resend in its original task, retaining the factual time boundary, then check the stored resend. Do not restart domain work, repeatedly wake tasks, or claim a pre-send guarantee: this integration sees the final after it has streamed.
