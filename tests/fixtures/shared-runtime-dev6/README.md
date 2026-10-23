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
