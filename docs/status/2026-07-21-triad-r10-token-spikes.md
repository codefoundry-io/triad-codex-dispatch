# R10 token-using functional spikes

Date: 2026-07-21 Asia/Seoul

## Google-family route

- Route: candidate `bin/antigravity_wrapper.py` through the owner's authenticated `agy` CLI.
- Model: exact `gemini-3.1-pro-high` (`Gemini 3.1 Pro (High)`).
- Sandbox: `read-only`.
- Timeout: 240 seconds.
- Result: wrapper exit 0, vendor exit 0, elapsed 7.9 seconds.
- Exact answer: `TRIAD_AGY_R10_SPIKE_OK`.

## Fresh Codex route

- Native task: `/root/r10_codex_token_spike`.
- Context: `fork_turns="none"`; no inherited task history.
- Model: `gpt-5.6-sol`.
- Reasoning effort: `high`.
- Scope: read-only functional coherence check of the formal dependency, validation context,
  shell-entry preflight, and documented approval behavior.
- Exact answer: `TRIAD_CODEX_R10_SPIKE_OK`.

## Bound executable candidate hashes

```text
3690b6094792bdd6ae8d659571822e914309f1df3e8577ad0419503755446f5a  requirements.txt
c8db6406af074baf19edadae90b109646dc0f181a39a1152e50025b46543305c  bin/_common.py
720e31856d4f8319f3850f752698370a9785497c21ba399a4dac8260e01ac2bd  bin/_pty.py
450bdcd0f54611ac9e7d2e8927b14fc4750220cc09207df7e0c2a64571d51ec0  bin/antigravity_wrapper.py
7999a5a51fa3ad73f16acdf86207d2355132be34e9568b7f8bea1d9fe20a75db  bin/bootstrap_repair.py
```

After the spikes, only two README troubleshooting anchor links were added; no executable or
dependency bytes changed. The resulting candidate then passed:

- macOS: `588 passed, 6 subtests passed` in 118.26 seconds.
- pinned Ubuntu 24.04: `587 passed, 1 skipped, 6 subtests passed` in 75.14 seconds.

The R10 packet snapshot must include this document and the executable hashes above must match its
frozen candidate before dispatch.
