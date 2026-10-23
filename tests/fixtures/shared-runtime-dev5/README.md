# Frozen dev5 library fixture

`library.zip` contains the exact 26 package/license files and adoption
record from Codex commit `89acf3a7c3deda49d0e48942020e5061e638aa61`.
Library version: `0.1.0.dev5`; source: `859f27c07c1123e87b50344f587999a0cbc172a6`.
All files were checked against Git blobs, adoption hashes, and the complete
package/license Git tree. Archive SHA256: `6d36cba0869ef73a9da315a0fdc53f391421966a81f0f47924453702df798b5e`.

Tests combine these frozen library bytes with a synthetic current-host toolkit
and fake wrappers. This is prior-library migration coverage, not a full old-host
or real-provider execution claim. Extraction checks the pinned archive digest
and exact inventory and writes only validated relative members; no network or
dependency installation is used.
