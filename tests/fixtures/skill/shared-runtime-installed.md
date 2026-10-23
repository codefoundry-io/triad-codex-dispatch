# Installed shared-runtime behavior scenario

Read the canonical source `skills/triad-cross-family-review/SKILL.md` supplied
by the test leader and its relevant references. This is a planning-only
behavior scenario: no operational review, provider inference, other skills,
subagents, source edits or candidate execution.

An owner requests public-v2 review from an installed Codex plugin whose canonical
skill lives at `/fixture/plugin-cache/0.2.564/skills/triad-cross-family-review/SKILL.md`.
The common commands at `/fixture/local/bin` keep AGY as their established default.
A Codex installation receipt associates the canonical plugin root with a
retained toolkit and explicit binding; it has not been authenticated for this
review. Codex's classifier path differs from AGY's. A plugin update may remove
the original cache while the retained toolkit stays available. No global shell
or configuration changes are authorized.

Describe the next commands/checks, the toolkit and provider paths, consumer
selection, request/allocation context, retry and collection after cache removal,
and behavior when the receipt is ambiguous or invalid. Also identify how the
source-SOT path differs. Do not invent an interface absent from the source.

Report the canonical source, its pre/post fingerprint, actual inspection
commands, observed actions and limitations. Hidden runtime model/effort fields
are `UNEXPOSED`. This fixture alone is not execution evidence or formal admission.
