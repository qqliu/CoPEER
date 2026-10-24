# Final audit contract

Write final semantic evidence to `audits/<cohort>_final.json` as a JSON list, and optional textual corrections to `corrections/<cohort>_final.json`. Draft/compile/helper files are not final semantic evidence. Every assigned ID must occur exactly once across final files. Use original index IDs (the loader normalizes only `Graph Theory_` to `Graph_Theory_`).

Each row must contain:

- `record_id`
- `confirmation_status`: `CONFIRMED`, `EXCLUDED`, or `UNRESOLVED`
- `source_fidelity`, `witness_validity`, `lean_fidelity`: explicit `PASS`, `CONFIRMED`, `FAIL`, `UNRESOLVED`, or `NOT_APPLICABLE` for no Lean. Put explanations in separate fields or use an object `{status, evidence}`.
- `release_decision`: `RETAIN` / `EXCLUDE` (retention remains contingent on fresh final build).
- `witness_action`: `KEPT`, `REPLACED_INVALID`, or `NO_VALID_REPLACEMENT`.
- `original_witness`: exact original packet text; `current_witness`: exact revised text (same if kept).
- For replacements: `original_witness_failure`, `same_source_claim_and_hypotheses`: `PASS` or `CONFIRMED`, plus detailed justification. Valid original witnesses must be kept.
- `error_categories`: list of human-derived categories (with explanatory evidence).
- `source_packet`, `source_packet_sha256`, and `source_check`, `counterexample_check`, `lean_semantics_check`, `mathlib_reuse_check`.
- `lean_path` (repository relative, null if originally absent), `lean_sha256`, `final_theorems` (list of exact fully qualified declaration names).
- `corrected_fields`: optional problem/claim_quote/flaw/witness/explanation changes; do not rewrite original source evidence.
- `remaining_limitations`, `human_verdict_changed`: false.

Never invent a PASS to satisfy the schema. Final retained records must be confirmed against the same full source claim and assumptions, with valid witnesses, faithful mathematical objects in Lean, and fresh successful compiler/axiom evidence for the exact selected theorem and input hashes. Exclusions preserve all historical evidence. Original human YES decisions do not transfer to revised artifacts. A compilation result alone is not semantic confirmation.

## Correcting witness prose without changing its mathematical values

For `KEPT` records, retain `original_witness` and `current_witness` as exact original packet text. If auxiliary claims in that paragraph are wrong or unsupported, set `published_witness_text` to corrected prose, `witness_values_unchanged` to `PASS`, and provide both `witness_text_correction_reason` and `witness_values_preservation_evidence`. The renderer publishes the corrected prose and preserves the original in the ledger. This is not a route to substitute a valid witness; changing mathematical values still requires `REPLACED_INVALID` with the original failure and the same full source claim.
