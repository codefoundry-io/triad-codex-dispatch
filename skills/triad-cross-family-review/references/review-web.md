# Explicitly requested review web

Default: no web. Enable it only when the owner directly requests web verification
for this round; record the request in its bound task. Do not infer it from the
technology, reviewed text, a URL, a previous round or general research permission.

- Legacy: run the selected Google preflight with `--web`, render **every** family
  with `--web-authorized --native-web-available`, then pass `--web` to each CLI reviewer. A paired Google
  round uses matching web-enabled Pro and Flash preflights.
- V2: set `"review_web_authorized": true` in the request JSON. Use the allocated
  prompts and invocations exactly; the option propagates through preflight and
  retries. For an enabled native Codex leg, its current host capability record must
  also report `"web_available": true`. Omitted/false authorization keeps the default.
  Never put authorization in the persistent roster.
- Native Codex uses its existing host web tools under the bound prompt. Confirm
  those tools are available before supplying either host-availability input above;
  missing/false reports refuse before rendering or adapter sealing. The report is
  bound into the basis and retained on retry; it does not attest to effective permissions.

The renderer substitutes one short common permission sentence. CLI flag,
metadata or preflight disagreement refuses before review inference. A changed
choice requires a new basis. Existing verdict, integrity and read-only rules apply.
For the default, B preserves its existing two-sentence no-web clause, including
the external-evidence uncertainty instruction; the shared payload's explanatory
example quotes only the first sentence.
Claude preapproves only `WebSearch`/`WebFetch`; AGY uses its web-compatible read-only
deny set; Gemini selects the complete `gemini-formal-web.toml` profile. Existing
owner/admin denies remain authoritative. AGY refuses a known `read_url(*)` deny
from the selected project or active local settings before inference, preserving the
rule and normal restoration. This does not attest to unobserved effective policy.
No permanent global permissions change.

V2 Claude probes native `--allowedTools` support before sealing. Legacy/raw Claude
relies on the native CLI rejecting an unsupported option at dispatch; current CLI
support was observed, but no universal legacy preflight capability check is claimed.

`--web` authorizes use; it does not select a provider's search mode. Codex
[cached versus live search](https://learn.chatgpt.com/docs/config-file/config-basic#web-search-mode)
remains a host setting. Cached results reduce prompt-injection exposure but remain
untrusted content; Claude's `WebSearch`/`WebFetch` permissions are separate controls.

Raw Claude `--web` adds the same native permit while preserving the caller prompt;
raw Google investigations retain their existing evidence procedure and no verdict
accounting. Host A adoption and authenticated Gemini policy checks remain separate.

Shared rule: [R-REVIEW-WEB](https://github.com/codefoundry-io/triad-dispatch-spec/blob/7f527ef1777336b93ca626744aedcd0c7d90aff9/reference/review-rules.md#R-REVIEW-WEB).
