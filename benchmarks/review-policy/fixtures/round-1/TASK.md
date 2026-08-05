# Focused review benchmark, round 1

Review every case below for correctness, cross-file propagation, and
configuration/documentation compatibility. Treat each case as independent.

- `clean/`: renaming the returned key from `legacy_name` to `display_name`
  must preserve the documented value and is the clean control.
- `local_defect/`: `validate_count` returns `False` for non-integer or negative
  values and `True` for zero or a positive integer.
- `cross_file/`: `authorize` grants access only when `parse_token` returns a
  non-empty token.
- `config_doc/`: the packaged retry limit must equal the governing documented
  default.

Inspect the complete files and `REVIEW.diff`. Report only source-grounded
findings. Do not execute any file.
