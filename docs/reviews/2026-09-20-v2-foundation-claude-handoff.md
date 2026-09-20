# B v2 foundation: Claude-host handoff

Shared basis: [055204c83e57bf87eeac5b2422f2b17340f7c53b](https://github.com/codefoundry-io/triad-dispatch-spec/commit/055204c83e57bf87eeac5b2422f2b17340f7c53b),
a published candidate, not tagged adoption. A source observations below are pinned
to `codefoundry-io/triad` commit `92c8afd500499d8736afcc28b39a87a4f87fed50`.
A is read-only during B-first implementation; this is an adoption review request,
not a claim that its maintainer accepted or implemented the candidate.

## B implementation and A impact

| Surface | Current A evidence | B change / A adoption guidance |
|---|---|---|
| Binding | [Legacy model lines 523–547](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/3rd-Agent/wrappers/verdict_schema.py#L523-L547) has only review ID, family and digest | B `bin/validate_v2.py` provides an explicit offline route checking those plus leg name, attempt and route. Add a separate v2 path; preserve legacy APIs. |
| Original JSON | [Ordinary file validation lines 304–339](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/.claude/skills/triad-cross-family-review/lib/validate_verdict.py#L304-L339) uses last-wins `json.loads`; [raw admission lines 583–607](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/.claude/skills/triad-cross-family-review/lib/validate_verdict.py#L583-L607) already rejects duplicates | Apply duplicate checks at the original-text v2 boundary before lossy parsing. Preserve A's end marker/two-pass admission and shape-only legacy API. This does not establish a bypass in the raw admission path. |
| Roster | [Loader lines 2618–2623](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/.claude/skills/triad-cross-family-review/lib/review_scratch.py#L2618-L2623) is the optional-leg v1 format | B vendors the shared named-roster schema but does not activate its consumer in this slice. Both hosts must switch every shaped prompt/renderer/collector together when v2 dispatch is ready. |
| Distribution | [Generic export lines 120–129](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/3rd-Agent/export_plugin.py#L120-L129) includes the validator; [distinct codex-host list lines 678–701](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/3rd-Agent/export_plugin.py#L678-L701) has a different file set | B adds exact contracts, manifest and validator to archive hash checks. A should verify its intended export product rather than infer packaging from source presence or from the other export. |

B reuses the canonical-file reader and original-member check in its unchanged
legacy validator. New `requirements.txt` declares `jsonschema>=4.26,<5` and its
directly used `referencing>=0.28.4` API;
`bin/bootstrap_repair.py::formal_schema_dependency_ready` refuses an unavailable
API before persistent installation. No dependency is installed implicitly.
`scripts/verify_distribution.py::HASH_TARGETS` binds the new payloads to archives.

## Features preserved and verification

Preserve A's native Claude, restrictive subprocess invocation, end marker and live
AGY read audit; preserve B's native Codex, copied legacy gate and dormant hook.
Neither host may fabricate missing v2 coverage, findings or uncertainty from v1.
No provider SDK or custom schema engine is introduced. Library reference:
[jsonschema validation](https://python-jsonschema.readthedocs.io/en/stable/validate/)
and [offline reference configuration](https://python-jsonschema.readthedocs.io/en/stable/referencing/).

The B test matrix covers original duplicate members, required/extra fields,
verdict/evidence consistency, every binding axis, both Google routes, missing or
altered payloads, manifest provenance, offline retrieval refusal, legacy copied-file
isolation, bootstrap no-mutation refusal and distribution hashes. macOS/Ubuntu
receipts and the complete required review gate must establish completion; code
presence alone does not. Authenticated identity, V1–V5 and full v2 dispatch are
not verified by this foundation. D-B1/D-B2 remain unresolved owner choices.

B's new CLI uses standard JSON ASCII escaping so contract-valid escaped Unicode
values remain serializable on UTF-8 stdout. A's [raw-admit artifact writer](https://github.com/codefoundry-io/triad/blob/92c8afd500499d8736afcc28b39a87a4f87fed50/.claude/skills/triad-cross-family-review/lib/validate_verdict.py#L628-L669)
already uses default escaping; its ordinary validator emits no success object.
No corresponding A admission change is needed. Provider stdout paths use different
serialization, but their acceptance of the reproduced value was not verified;
do not treat that observation as a confirmed A defect or change raw replies.

Bundle failures name the damaged contract separately from a bad operator result;
schema error messages expose no raw value. A does not yet load this bundle, so
there is no matching bundle diagnostic to repair in its legacy validator.
When adopting the loader, carry the same error attribution and explicit direct
dependencies. The referencing lower bound matches
[jsonschema 4.26's declared dependency](https://github.com/python-jsonschema/jsonschema/blob/v4.26.0/pyproject.toml).
