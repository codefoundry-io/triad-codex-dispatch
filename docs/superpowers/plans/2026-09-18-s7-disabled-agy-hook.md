# S7: Disabled AGY allowlist helper implementation plan

> Use Superpowers TDD with separate fresh Terra/high RED and GREEN executors.
> The root leader owns source/tests; independent agents execute and review.

**Goal:** Package an offline-testable PreToolUse name allowlist and a disabled
configuration renderer, without changing the active review environment.

**Architecture:** One standard-library helper consumes documented JSON stdin and
emits a fixed decision. A separate CLI option prints a disabled configuration.
The current wrappers, launcher group, project guard and admission stay unchanged.

**Spec:** `docs/superpowers/specs/2026-09-18-dispatch-adoption-design.md`, S7.
**Source:** https://antigravity.google/docs/hooks

## Contract and budget

Create `bin/agy_hook.py` and `tests/test_agy_hook.py`; add the helper to the
existing distribution hash inventory and synthetic distribution test inventory.
Update English/Korean README and SECURITY. Expected production additions below
100, novel core below 100, tests about 130, documentation about 90 lines.
Python >=3.12, no new dependency, version change, installer or bootstrap wiring.

`decide(payload: object) -> dict[str, str]` requires object/toolCall/name/args
shapes. Exact names `view_file`, `grep_search`, `list_dir`, `find_by_name`,
`search_web`, `read_url_content` return allow; all others return deny. No aliases,
whitespace/case normalization or input reflection. Paths and URLs are not opened.

`handle(raw: bytes) -> dict[str, str]` accepts strict UTF-8 JSON <=1 MiB;
malformed, deep, duplicate-member or invalid-shaped input returns deny. The CLI
reads at most limit+1 bytes and prints one JSON response with exit 0 for handled
decisions. Process crashes/timeouts have no claimed provider permission outcome.

`render_disabled_config(script_path: Path) -> dict` returns one named hook,
`enabled:false`, `PreToolUse`, matcher `*`, command type, timeout 5 seconds.
Shell-quote `python3` and the resolved helper path with `shlex.join`. CLI
`--render-config` prints that object; it never writes a hook configuration and
has no activation option. Default CLI reads stdin; it never invokes tools.

This is a name filter, not path/content/egress containment. Explicit allow is
not permission-neutral. Live discovery, normal read, off-list deny/no effect,
and preservation of existing deny rules require separate authorized activation
proof at the exact existing UUID/cwd. Keep disabled without that proof.

## Task 1: JSON adapter and packaging

- [ ] Write real subprocess tests for allowed/denied names, malformed/duplicate/
  deep/oversize input, fixed non-reflecting output, no fixture writes, disabled
  renderer and shell-special path round-trip. Example acceptance:

  ```python
  result = subprocess.run([sys.executable, str(SCRIPT)],
      input=b'{"toolCall":{"name":"run_command","args":{}}}',
      capture_output=True, cwd=tmp_path)
  assert result.returncode == 0
  assert json.loads(result.stdout)["decision"] == "deny"
  assert list(tmp_path.iterdir()) == []
  ```

- [ ] Fresh dedicated executor runs `tests/test_agy_hook.py` and
  `tests/test_distribution_verifier.py` to observe missing-helper/inventory RED.
- [ ] Implement the bounded helper and hash target entry, then public guidance.
- [ ] Separate fresh executor runs focused GREEN, full suite, source validator
  and packaged provider-free lifecycle once; retain terminal records and exact
  source/fixture identity. No live hook activation or clean archive claim.

## Task 2: Gate and merge

- [ ] Independent static task review; root validates any findings and makes only
  necessary in-scope fixes. Freeze source for the required four-leg gate.
- [ ] Complete integrity/admission, CI, remote/source/protected-state checks and
  owner-authorized merge. Continue S8; ask the owner only before deployment,
  except at the owner's confirmed-design-defect stop boundary.

Verification uses literal `python3` from the host login shell, canonical source
paths/rootdir, `PYTHONDONTWRITEBYTECODE=1`, and pytest `-p no:cacheprovider`.
Full suite: `python3 -m pytest -q "$1/tests" --rootdir "$1" -p no:cacheprovider`.
Resolve the host system skill validator; invoke source
`skills/triad-cross-family-review/scripts/verify_lifecycle.py` once, without
`--help`. Keep deployment proof distinct from source verification.
