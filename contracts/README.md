# Shared contract candidate

These three JSON Schema Draft 2020-12 payloads are byte-identical to
[shared commit 055204c](https://github.com/codefoundry-io/triad-dispatch-spec/commit/055204c83e57bf87eeac5b2422f2b17340f7c53b).
`source-manifest.json` is host-owned provenance: source repository, exact commit,
candidate status and per-file SHA-256. It is neither a revision tag nor a signature.
Changes to shared semantics must first be published and reviewed in the shared repo.

`bin/validate_v2.py` checks the bundle and validates original verdict JSON offline
with the maintained [python-jsonschema library](https://python-jsonschema.readthedocs.io/en/stable/validate/).
An explicit empty [reference registry](https://python-jsonschema.readthedocs.io/en/stable/referencing/)
prevents remote/file retrieval. The host also rejects original duplicate members
and compares all six expected invocation bindings. It returns the validated data
without converting legacy labels or filling absent evidence.

Only verdict validation is exposed here. Roster/receipt consumers and complete
v2 dispatch activation follow separately; their bundled schemas are not claims
that those operations are implemented. Existing wrappers, custom schemas and
the copied standalone `bin/verdict_schema.py` legacy gate remain unchanged.
Installing this candidate does not change a deployed `SPEC_REVISION`, confer
admission or establish live CLI enforcement. V1–V5 remain separate checks.
