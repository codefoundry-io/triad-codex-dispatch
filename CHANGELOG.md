# Changelog

## 0.2.464 — 2026-07-06

**Repair privilege-separation redesign.** The self-improving classifier's
repair path is now split so the component that reads an untrusted vendor
run-log has zero write authority:

- This codex-host product ships **no in-session repair worker** (a codex
  subagent would inherit the leader's sandbox and could not be confined).
  Repair is a top-level `codex exec -s read-only` analyzer you paste into a
  fresh terminal — it can only read.
- The analyzer's proposal is applied ONLY by the **deterministic, zero-LLM**
  `bin/apply_patch.py`. The generated profile also pins
  `features.multi_agent = false` as a backstop.
- Ships a **SECURITY.md** documenting the threat model, the control, and —
  explicitly — what is NOT the control.

README polish: value-first opening, a copy-runnable first-dispatch example,
a plugin-only (no-clone) verify path, a troubleshooting + exit-code section,
and an honest scope-&-limits list.

Built from the Triad source of truth. Full history: https://github.com/codefoundry-io/triad-codex-dispatch/commits/main (each release commit summarizes its delta).
