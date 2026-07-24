# R11 token-using functional spikes

Date: 2026-07-21 Asia/Seoul

## Google-family structured-output route

- Route: current candidate `bin/antigravity_wrapper.py` through the owner's authenticated
  `agy` CLI.
- Model: exact `gemini-3.1-pro-high` (`Gemini 3.1 Pro (High)`).
- Sandbox: `read-only`.
- Input: immutable R10 packet and its exact digest, used only as a transport/schema fixture.
- Result: wrapper exit 0, vendor exit 0, elapsed 12.0 seconds.
- Validated answer:

```json
{"review_id":"20260721-triad-reliability-final-r10","packet_sha256":"8124db85fdfaec7226f1bd25eede6689d6fa0f799174bdd336b798887a124e84","verdict":"SAFE","findings":[],"open_questions":[]}
```

This proves that trusted packet context remains available while the complete `FormalReview`
envelope instruction is effective at the end of the prompt.

## Fresh Codex route

- Native task: `/root/r11_codex_token_spike`.
- Context: `fork_turns="none"`; no inherited task history.
- Model: `gpt-5.6-sol`.
- Reasoning effort: `high`.
- Scope: read-only check of the audit-redaction launcher pin, exact ownership recognition,
  prompt assembly order, and focused regressions.
- Exact answer: `TRIAD_CODEX_R11_SPIKE_OK`.

## Bound executable candidate hashes

```text
3690b6094792bdd6ae8d659571822e914309f1df3e8577ad0419503755446f5a  requirements.txt
c8db6406af074baf19edadae90b109646dc0f181a39a1152e50025b46543305c  bin/_common.py
720e31856d4f8319f3850f752698370a9785497c21ba399a4dac8260e01ac2bd  bin/_pty.py
fffc697f488f2a0d8dbe247d5cc60fbd59aeec301e2db84d2056a8f67f0d30b0  bin/antigravity_wrapper.py
cc4c55573e6feabf04ee8cf7ff7c2fb9e40e52b446d54efebc33a796c005170a  bin/bootstrap_repair.py
18bea59967bfe8eba88588f8e789d3a6d29b6b70f42f34c776d4def66ef51d48  scripts/bootstrap.sh
```

Focused regression result: `7 passed`. The focused prompt review is recorded in
`docs/status/2026-07-21-triad-r11-prompt-review.md`.
