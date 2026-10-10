# U2 initial authentication evidence map

Basis: B 632f426 plus preserved dirty candidate; shared main 3afc4d7,
clarification PR13 11c6b46. Initial source observations below are separate from
the subsequently completed U2a proof (shared b085a6e). Existing AGY credit-carrier
research is reused without inference.

| Case / requirement | Current B evidence | Next bounded verification |
|---|---|---|
| C11 / C17 environment removal | `bin/_common.py:scrubbed_child_env` removes interpreter/loader injection; provider tests cover formal Google auth scrubbing | Compare the exact shared environment set and set each candidate variable synthetically; do not read credential values |
| C16 Gemini floor | Previous Google unit owns the 0.63.0 floor and its passing tests | Reuse its proof; do not repeat a provider probe on installed 0.60.0 |
| C37 / DL-75,92 authentication carrier precedence | `classify` returns success/timeout first and otherwise searches merged stdout/stderr text after capacity, except the AGY banner | Map measured vendor error envelopes and quoted-answer controls before any order change; changing phrase order alone is insufficient |
| C37 / DL-99 Gemini exit 41 | U2a implemented and reviewed: `_authentication_exit` recognizes Gemini 41 before other failed-run decisions and preserves it across signals | COMPLETE for this code carrier: 1925 full-suite passes / 4 skips, fresh all-four SAFE. Broader C37 remains open |
| C37 / DL-95 interrupted authentication | `_mark_signal_failure` overwrites classification with unknown; existing parent-signal tests cover cancelled success | Reproduce a captured auth result followed by a signal while preserving existing no-success and child-reaping controls |
| C43 vendor phrases | `tests/test_vendor_quota_contract.py` covers two CLI-specific quota phrases and explicitly disclaims all-carrier conformance | Retain completed quota work; AGY credits output location/exit remains unmeasured |

A read-only comparison at 0e04d2a identifies `_auth_carrier_stop` and its Gemini
exit-41 branch in `3rd-Agent/wrappers/_common.py`. It is evidence for the intended
carrier separation, not an implementation to copy as authority. B's unused raw
Codex compatibility path and A's external Codex route must not be confused with
B's native Codex spawning.

Next: write a bounded U2 carrier manifest with exact source/capture provenance,
then RED cases for demonstrated gaps. Estimate code scope after mapping the
existing extractors and callers; preserve result types, terminal records, no
automatic authentication retry, and signal cleanup. No AGY quota carrier fixture
may be invented. Optional U1c stays deferred under R-AGENT-ROLES/C73.
