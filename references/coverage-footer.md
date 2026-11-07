# Optional coverage footer — disabled by default

User-requested — 2026-11-07: “Can we try disabling? Maybe move to another file or something?” Keep this rule ready to bring back straight away if requests seem to be ignored again. Disabling the visible counts is a trial, not evidence that OpenAI fixed omissions. The normal duty to read every meaningful request and check the actual final reply stays active.

## Restore or disable

When the user says “bring back coverage” (or equivalent), follow this reference for the requested scope immediately. For a lasting preference, change the coverage status in the core's **Closing reminder and notification** section to enabled and link here; do not reconstruct the counting rules or restore an older whole skill. Update the public explanations and affected examples through the normal maintenance workflow. An explicit per-reply request needs no persistent edit. To disable it again, set that core status back to disabled. No program, automatic repair or hook is needed.

## Enabled behaviour

Only when enabled, put one ordinary-text coverage line immediately underneath the final lavender About reminder. A required project footer retains its established position after that pair. Never print coverage in commentary, progress updates or skill announcements.

Use ordinary text for the coverage line: `Coverage since last final reply: N user messages; Y/X requests and steers addressed.` The window starts immediately after the previous assistant final reply, or at the start of the chat for its first final reply, and ends at this final reply. Count every human user message in that window, including interruptions, corrections and steering; exclude automatic context, system messages and tool output. Commentary and tool calls do not reset the window. Never choose an arbitrary set of older messages or reuse the accumulated task-checklist total.

Within that window, privately list each distinct question, requested action or steer and map every item counted as addressed to the exact sentence or bullet in this final reply that answers it, reports its verified action or states its unresolved status. Combine repeated or closely related wording by meaning; one answer may cover several items. Following a constraint silently is not an explicit answer in the final reply. A plan or an answer only in an earlier reply does not count as addressed here, and an acknowledged unknown is not proof of completed work. Do not inflate the total with internal implementation steps. Never invent a count or a perfect score; identify what remains unanswered when Y is smaller than X. Keep unfinished work from earlier windows tracked separately without adding it to this window's counts. Track this privately during work and print the line only in the final reply. This is a manual semantic check, not an automatic counting/repair hook or a guarantee of model obedience. User clarification — 2026-10-13: count messages and steers since the last final reply, not an arbitrary part of task history.


## Optional diagnostic

The existing `scripts/check-reply.py --require-question-coverage <draft.md>` requires the enabled footer and validates its form, arithmetic bounds and placement. Without that flag, a final About reminder needs no coverage line. The diagnostic cannot count real requests or guarantee model obedience; it remains optional, not a step for every reply.
