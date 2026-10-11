# Claude maintainer handoff prompt

**Follow-up status, 2026-10-09:** The original prompt below has been answered in
PR #13 comments `6073991579` and `6074188589`. Do not resend its completed
requests. Current baseline: main `3afc4d7`, PR #12 `6a2883d`, PR #13 `5c040ff`;
A source `49910604`. Gemini floor and DL-131 edits are observed in source/spec;
A's test execution and AGY equals-form dispatch remain maintainer-reported.

Remaining handoff, if the owner chooses to send it:

> Your DL-132 transport agreement is recorded; finalize R-MODEL/C18/C34 around
> opaque values, with encoding measured per parser. Please link the existing
> sanitized AGY 1.3.2 capture/path and hash if available, without rerunning it.
> It proves the ordinary pin used, not option-shaped values or Claude parsing.
> DL-133's C34 wording needs to distinguish the selection call before review
> inference from identity exposed by the review call itself; neither unexposed
> identity nor effort should be invented. Codex U1a is already corrected and
> reviewed (99 affected tests, four SAFE results; PR #13 `5c040ff`), so reconcile
> its stale OPEN-B diagnostic status. Keep C16/C18/C65 A-test re-pins after PR #13
> and outstanding historical annotations tracked. No native-leg change requested.

The historical prompt below asks for source work and
shared-contract review on that host, not a review verdict for Codex's whole
candidate. Neither side's native leg is in scope. PR heads can advance; refresh
them before responding.

---

We are both implementing the same shared specification concurrently. Please
continue your Claude-host work and review the current shared main plus PR #12
and PR #13 together. Treat an unimplemented requirement as pending work unless
specific evidence establishes a defect. Do not treat either host's implementation
as automatically correct, and do not change Codex code or either native leg.

Entry points:

- https://github.com/codefoundry-io/triad-dispatch-spec/pull/12
- https://github.com/codefoundry-io/triad-dispatch-spec/pull/13
- `decisions/2026-10-09-execution-planning.md` on the PR #13 branch.
- Last baseline reviewed by Codex: main `3afc4d7`, PR #12 `1a5ab9a`, PR #13
  `32d7897` (selection-observation clarification; see its later U1a completion
  follow-up on the same PR); your source `32124be` plus
  concurrent dirty changes. Resolve the latest heads rather than pinning to these
  historical observations.

Please handle the following, preserving work already in progress:

1. **Gemini minimum:** apply the owner-selected common `>=0.63.0` boundary to
   A's raw, legacy and v2 Gemini paths. Keep the no-catalog rule and required
   auth/containment/capability checks. Report C16/C18/C65 boundary evidence,
   including a floor prerelease, below-floor version and previously unlisted
   pin. If already implemented, give the new commit and tests instead of redoing it.

2. **Model-value transport:** review the new evidence under R-MODEL. Gemini
   0.63.0's actual isolated parser reinterprets `--model --help` as help;
   equals-form values remained exact in the tested cases. Codex's three actual
   Python wrapper parsers were also checked: separate `--help`/`--yolo` values
   exit 2 before dispatch; equals forms parse exactly. This proves a transport
   boundary issue, not a shell-injection or privilege-escalation finding.
   Inspect A's corresponding argv boundaries and decide whether existing C18
   already expresses the intended behavior or needs a shared clarification:
   preserve one opaque model value, without a new model-name allowlist/grammar.
   Check real AGY/Claude parsing before assuming equals encoding is universal;
   help-only output does not reveal the parsed model.

3. **Codex Claude-adapter C34/R-MODEL semantics:** Codex has fixed the three
   reproduced catalog/selection defects and two subsequent header-parsing
   findings. Final affected tests: 99 passed; fresh round
   `triad-claude-selection-20261009-r2` returned four SAFE results with matching
   integrity. This is a local uncommitted candidate; alias defaults subsequently
   completed under U1b, and A's native leg is unchanged. Please review the shared
   interpretation needed for removal of catalog gating: requested model/effort
   stay unchanged, known contradictory selection refuses, and unknown selection
   labels/effort exposure must not become invented identity/capability claims.
   R-ROSTER currently names B's pre-inference selection check, while R-MODEL
   forbids model-availability probes. Identify the intended distinction and
   any missing case for unexposed identity/effort. Do not remove a required guard
   or authorize an extra paid probe implicitly. This is contract review, not a
   request to add a Claude CLI route to A.

4. **Documentation reconciliation:** finish the shared changes recorded by
   DL-110/121 and DL-124..126. Keep `task-blocked` in the contract but identify
   B's external Claude wrapper as its producer; correct A's extractor count and
   C35/37/43 references, plus the obsolete hook/stream/audit pointers in
   C1/C23/C36 and historical DL rows. Confirm exact surviving test names/counts.
   Codex found no new B port for DL-124..126; its finding is limited to the
   described mechanisms, not total stream-admission equivalence.

5. **AGY evidence limits:** credits wording is documented but its exact
   channel/event/exit is still unknown. Do not exhaust quota or fabricate a
   fixture; provide an existing capture/source only if new evidence exists.
   DL-103's old B null-enum diagnosis is stale: its actual bound AGY v2 schema
   now has route `['agy']`. Remaining live keyword compatibility is NOT RUN.
   A's broader projection does not prove that all removed keywords are rejected
   by AGY; distinguish AGY evidence from Codex-vendor evidence.

6. **Review discovery and log inspection (C70/C71):** read shared
   `decisions/2026-10-09-review-read-boundary.md`. At A `a91b436`, Codex found
   related unchanged inspection supported and no exhaustive source allowlist.
   B corrected its operational exact-file-only packet and routine source-path
   log audit. Confirm the shared clarification: diff/packet lists are entry
   points, reviewers discover related code, and leaders inspect logs for concrete
   incidents rather than normal source-read approval. Preserve A's coded AGY
   required brief/patch-read, tool-effect and hook checks; no native-leg change.

7. **AGY search exposure:** shared `decisions/2026-10-09-agy-search-tools.md`
   records B's Pro coverage failure and AGY 1.2.7's removal of grep_search,
   list_dir and find_by_name from the default toolset (current binary 1.3.2).
   A source 9e16880 already supplies an explicit tools profile. If existing
   current-version evidence exists, provide actual search success and definition
   lookup/hash; no need to change your native leg. B's owner approved the profile
   design/implementation; global installation retains a separate exact-path gate.
   No silent A-profile reuse is planned.

   **Reply received:** [PR13 comment 6075351927](https://github.com/codefoundry-io/triad-dispatch-spec/pull/13#issuecomment-6075351927).
   A confirms global lookup and init.agent selection on 1.3.2. init.tools listed
   60 names including off-profile tools; no actual tool call or retained current
   native-search success exists. Do not request another A paid probe now: B will
   verify its own path after approved setup. This is now complete: explicit
   setup preserved A's profiles, and one AGY 1.3.2 Pro/high formal-v2 call completed
   native grep_search then view_file with real global lookup. Wrapper/vendor
   exit 0; scope is that no-web fixture. Fresh U1b+C72 R3 then returned all four
   SAFE with matching integrity. The four documentation follow-ups are now
   corrected in six shipped files, including removal of the stale catalog gate.
   Fresh behavior verification plus 159 regressions and two validators passed;
   a separate documentation round is all four SAFE with matching integrity.
   Remaining wording suggestions were tested with fresh Luna/high: intended
   update/removal/missing-profile choices were correct, so no more wording loop.
   Optional test expansion and receipt-parser refactoring remain recorded;
   no new A native-leg work or paid probe is requested. Profile selection alone is not a
   containment claim. C70/C71 and U1a interpretation are agreed by A; C70/C71
   tests.A remains NOT RUN until A's planned case synchronization.

For every response item use:
`rule/case | pending/already implemented/spec clarification/unmeasured |
source commit + file/symbol | test and result | shared-spec commit | remaining limit`.
Record common facts, disagreements and necessary cases in the shared spec and
link the same commit in a PR #13 reply. Do not overwrite either branch's new
concurrent work. Settled implementation continues independently; only dependent
contract changes wait for agreement. Bring a substantial unresolved design
choice to the owner with concrete alternatives and effects.

Keep prompt guidance minimal and focused on contextual wrong decisions. If
wording/grammar nuance repeats without a concrete behavioral defect, use the
owner-requested fresh Luna/high scenario/control test where available, without
showing expected answers or review history. Correct choices end wordsmithing;
this does not replace required formal reviews. Do not merge, tag, release or
change global authentication as part of this handoff.
