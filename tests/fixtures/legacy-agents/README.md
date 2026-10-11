# Historical legacy-agent ownership fixtures

These files are inert test data, never installed or dispatched as agent definitions.
The six `307745f-*` and `dca0cd4-*` files are complete, unchanged Git blobs from
`agents/{claude,gemini,agy}-wrapper-repair.toml` at those revisions. Bootstrap used
`cp` for those variants. Tests exercise actual removal/quarantine and preserve edits.

`rendered-template.toml` is the full Claude template at `fee6f6f`. That installer
substituted machine paths and read grants without recording installed-byte receipts.
Tests construct a path-substituted example; it remains unmanaged. This does not
claim that any fixture was installed on the current owner's machine.
