# Independent review of twelve historical-certificate replays

**PASS, with one reporting-scope correction.** No Lean reruns or model calls were made in this review.

All 31 manifested artifacts match both SHA256 and byte count, with no unlisted artifact except the manifest itself. The 12 replay records equal the fixed 16 `REPLACED_INVALID` retained records minus the 4 with previously authenticated historical receipts. All 12 current release packets still match the frozen packet hashes and ledger. Removing exactly one final newline from dossier `Vlean` block 1 reproduces every recorded historical certificate hash, including the twelfth file whose recovered bytes retain two terminal newlines.

All 24 saved compile receipts report explicit exit 0, no timeout, and unchanged source hashes:12 under Lean 4.30.0 and12 under 4.34.0. Every axiom driver preserves its recovered source as an exact byte prefix and appends only blank lines and `#print axioms` commands. The axiom inspection itself uses 4.30.0; executable paths, version strings and commit IDs are retained, but executable SHA256 values were not recorded.

Independently removing nested Lean comments and strings and reparsing full axiom stdout accounts for all 123 theorem/lemma declarations: 78 with no axioms, 42 with `propext`, and 3 with `propext` plus `Quot.sound`. This includes the wrapped output for `Arxiv13041796v2SourceEnrichedCodex.refutes_sufficiently_large_displayed_inequality`. No `sorryAx` or native-reduction axiom appears. A separate lexical scan of comment-stripped sources found no `sorry`, `admit`, `axiom`, `native_decide` or `unsafe` token.

Three inspection drivers have exit 1, exactly because the extraction regex queried comment words: `above` at mse2605396 line 350, `records` at reddit1kehuzl line 26, and `is` at reddit14s0k9c line 8. The retained stdout contains exactly these three unknown-constant errors and complete axiom output for all actual theorem/lemma declarations. The 24 original-file compilation receipts all remain exit 0.

**Required wording correction before reuse:** README says “Every real declaration was inspected.” Use “Every theorem/lemma declaration was inspected for transitive axioms.” The files also contain 270 `def`, 12 `abbrev`, 6 `structure`, and 4 `inductive` declaration keywords that were not individually queried. This does not change the 123 theorem/lemma count or reported axiom sets.

This is evidence of **new reproducibility of exact historical bytes**, not authentication that an original historical build occurred. It is not a compiler false-positive count, a source-admissibility judgment, or a population frequency. Several old modules already contain an admissible result beside the disputed selected object; only per-record semantic adjudication identifies what was wrong or repaired.

Bindings and full per-record checks are in `HISTORICAL_REPLAY_INDEPENDENT_REVIEW.json`.

Replay manifest SHA256: `830355436b9eb31860a14ea8e123113eb415418a08d2abe8664b37cb0903e6a0`.

Fixed repair roster SHA256: `3e42bfa110bd79b1694e71959a3b7e5d7878271e109508d0f5e3590fc617c091`.

Review JSON SHA256: `8a928aedf030f512d5169273225f4f0899a4dd940a6c54fbe2237aa2b2fbe6b7`.
