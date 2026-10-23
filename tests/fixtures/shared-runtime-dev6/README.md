# Frozen dev6 library fixture

`library.zip` contains the exact 27 package/license files and adoption record
from Codex commit `2eec0bb62e0de027332b45c12e59fab94cf2bbc8`.
Library version: `0.1.0.dev6`; source: `1872227abd42553635c733e0aa228548a577a732`.
All members were copied from that commit's Git blobs. Tests independently check
the complete inventory and hashes before extraction.
Archive SHA256: `ea1ff46ef16e79d446abfc1d97f75c78eca81ca929466feafc8397a88a12082a`.

Tests combine these frozen library bytes with a synthetic current-host toolkit
and fake wrappers. This verifies prior-library migration, not a full old-host
or real-provider execution claim. No network or dependency installation is used.

`producer.zip` contains exact `bin/shared_runtime.py`, `bin/library_adoption.py`
and `bin/bootstrap_repair.py` Git blobs from the same commit, with archive SHA256
`3416c06224f415293d9503e562ff3b0f0470d4f043cfbf58ea7d77c271ea2ee2`.
The shared-generation regression verifies both archives before extracting them,
then executes this frozen producer in an isolated subprocess to create a real
dev6 generation. Other host files and provider observers are synthetic current-host
fixtures; the AGY legacy baseline is also synthetic and explicitly injected.
This proves old-generation migration compatibility, not a full historical host or
live AGY/provider deployment. Runtime verification reads old artifacts as bytes;
it does not execute the frozen producer or old library to verify them.
