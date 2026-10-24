# Saved corpus censuses and source categories

This addition supports the current 284-record documentation census and the earlier 401-record census, including all categories, negative labels, uncertainties, source strata, primary coding, corrections and the fixed 24-record assistant recoding sample. The current release has 18 recorded families and 70 recorded repairs; the earlier snapshot has 56 and 117. These are documentation labels, not counts of separately Lean-proved extensions. No new human judgments are introduced.

`records/` preserves all 284 annotation rows, the five fields they code, source/certificate identity operands, saved summary/status fields and table sources. `initial401/` preserves all 401 input/annotation rows, the full recoding/correction evidence and saved aggregates. Original operational paths have been normalized. Mathematical source text and source-author credit are preserved; no raw human reviewer returns or identity joins are exported. `tables/` contains exact table fragments extracted from the published 4e95dfc source. `reference78/COVERAGE.json` identifies the diagnostic already supplied by the instructions-study builder.

`CENSUS_INCLUSION_MANIFEST.json` records original and public byte hashes, transformations and exact paper bindings. The original analysis code is under each `source/`; it documents the original strict hash/roster/offset rules and may refer to research-tree inputs. `inspect.py` is a bounded portable saved-label/count check, verified during release integration; it does not call models, change labels, regrade proofs or recompile Lean. It is not a replay of the entire historical audit pipeline. The exporter prepared the files without running this check. During release integration, the documented command passed on the distributed files: 284 current records, 401 earlier records and the 24-record recoding sample match the saved counts and excerpt offsets. `REPLAY_VALIDATION.json` records the fresh check; the earlier audit evidence remains unchanged.

Historical source and annotation hashes are retained as provenance of original bytes; they are not asserted equal to anonymized public-file hashes. The current coded five-field text is byte-for-byte unchanged. Operational account tokens and directory prefixes are replaced with equal-length x characters in the earlier inputs: 401 `lean_path` metadata fields and five explanation fields. Filenames, string lengths, mathematical content and all checked excerpt offsets are preserved. `INTEGRATION_TRANSFORMATIONS.json` binds the preparation hashes to these final distributed files.

Run the bounded inspection from this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B inspect.py
```
