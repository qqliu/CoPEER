# Open-frontier paired rerun v2

Started: 2026-09-01 23:06:15 EDT

Stopped for migration: 2026-09-02 at approximately 12:00 EDT. All controllers
are stopped and the canonical lock directory is empty. Resume from the exact
validated boundary in `RESTART_HANDOFF_20260902.md` with
`qedbench_certificate_availability_triage/scripts/resume_open_frontier_paired_v2.sh`.
The copy-pasteable English operating instructions for Fable are in
`qedbench_certificate_availability_triage/FABLE_OPEN_PROBLEM_PAIRED_PROTOCOL.md`.

The requested four-hour progress checkpoint is 2026-09-02 03:06:15 EDT. The
experiment is incomplete and must continue on the replacement server until
every pair reaches a valid terminal state.

The active continuation rules are recorded in
`PROTOCOL_AMENDMENT_20260902_WHOLE_PROOF_STOPPING.md`. They remove the old
six-item claim-inventory cap and stop either arm at its first independently
verified full solution. `CLAIM_COVERAGE_CUTOVER_20260902.json` seals the exact
historical boundary without changing earlier artifacts.

This is a fresh rerun of all 31 open-problem targets. It does not overwrite or
reinterpret the legacy `open_frontier_loop` artifacts.

## Experimental unit

Each target receives one arm-neutral baseline draft. The exact same baseline is
then forked into two revisions:

- `plain`: native adversarial self-critique plus independently generated audit
  feedback;
- `bugbank`: the same audit feedback plus a mechanically generated, persisted
  BugBank retrieval receipt.

The baseline is not an outcome for either arm. A revision is classified as
BugBank-treated only when its receipt exists, its parent-claim hash matches the
baseline or prior revision, and its treatment log refers only to retrieved
entry IDs. Merely residing in a `bugbank` path is not treatment evidence.

The two revision arms use the same model and reasoning setting. A solver's
`FULL` label is only a claim. It becomes a verified full result only if an
independent audit checks every claim, finds no confirmed refutation, and the
writeup actually answers the recorded target. Verified claims in a `PARTIAL`
draft remain partial progress, not a solution of the open problem.

## Frozen treatment parameters

- model family: `gpt-5.6-sol`, with maximum reasoning effort;
- operational batch ceiling: 50 iterations after the shared baseline; this is
  extended and the run resumed if an arm has not met its stopping conditions;
- pre-cutover drafts and receipts used the original cap of six claims; those
  historical files remain sealed and are not rewritten;
- post-cutover drafts record every load-bearing claim in proof order, with no
  claim-count cap;
- post-cutover BugBank retrieval: `k=3` independently for every claim, using
  the exact claim statement, two newlines, and its exact proof sketch;
- BugBank statuses exposed: verified, draft, and seeded, with status retained
  on every hit;
- no source-item or entry-ID exclusions;
- full-precision BM25 order, broken deterministically by binary entry ID;
- the plain arm receives no BugBank text, retrieval result, or placeholder.

The all-status/no-exclusion choice reproduces the legacy retriever's treatment
scope. It does not imply that every returned entry is applicable or verified;
the revision must distinguish acted-on hits from explicitly dismissed hits.

## Stages

1. Generate an arm-neutral baseline without access to prior frontier outputs.
2. Audit every baseline claim independently.
3. Materialize a pinned BugBank retrieval receipt from the baseline claims.
4. Produce matched plain and BugBank revisions.
5. Audit every revised claim independently and verify any concrete witness.
6. Advance both arms independently. An arm stops immediately at its first
   strict independent audit of a full solution. A non-full BugBank revision
   that materially changes the proof or acts on a retrieved record becomes the
   parent of another complete retrieval/revision/audit cycle.
7. For an inconclusive result, require exact audited proof-state closure. An
   inconclusive plain arm must also reach the BugBank endpoint's token total;
   a verified-full plain arm need not do so.

A proof-state fixed point requires a complete audit, no confirmed refutation,
an accurate/non-overclaimed coverage judgment, and exact equality between the
parent and revision for `claimed_resolution`, the full ordered `results` array
(including every proof sketch), and `final_writeup`. Each audit separately
records whether the draft fully resolves the exact target, contains only valid
partial progress, makes no valid progress, or overclaims its scope. A fixed
point with any unresolved claim or without full target coverage is
inconclusive, never a verified full solution.

For an inconclusive BugBank endpoint there is one additional closure condition:
the terminal revision must have an empty `acted_on_entry_ids` list. A nonempty
list means the receipt changed or hardened the proof, and because that receipt
was generated from the parent draft, the resulting proof must be queried
against BugBank again in the next iteration. Retrieved records may be dismissed
only with a specific reason. This extra fixed-point condition does not delay a
strictly audited full solution.

Either arm stops at its first strictly audited full solution, even if the other
arm is unfinished. In particular, plain does not spend extra tokens merely to
match BugBank after it is already correct. If plain has no full solution, its
inconclusive endpoint still requires proof-state closure and cumulative
revision-plus-audit tokens at least as large as BugBank's endpoint total. Calls
are indivisible, so this matched-budget endpoint may overshoot. Shared baseline
and baseline-audit costs are excluded equally from both arms. Missing or
nonnumeric state telemetry fails closed rather than being treated as zero.

Once both endpoints exist, the pair terminal records both totals, plain minus
BugBank, and whether plain found a verified full solution using fewer tokens.
Calls completed after an already valid endpoint are preserved as historical
evidence but excluded from the endpoint totals.

The 50-iteration value is only a controller/schema bound. Reaching it without
a verified full solution or valid inconclusive endpoint is incomplete and
requires extending the bound; it is not a scientific terminal result.

Missing drafts, receipts, searches, or witness verification fail closed as
`INCOMPLETE`; they are never counted as negative results or fixed points.

## Artifact layout

- `baselines/`: neutral drafts shared by the paired revisions
- `retrievals/`: sealed, pre-cutover BugBank treatment receipts
- `retrievals_whole_proof_v2/`: post-cutover, uncapped whole-proof receipts
- `iterations/`: post-fork arm outputs
- `audits/`: independent claim audits
- `prompts/`: sealed prompt metadata for completed pre-cutover revisions
- `prompts_whole_proof_v2/`: post-cutover prompt metadata
- `states/`: machine-readable per-cell progress
- `pair_terminals/`: paired terminal states
- `logs/`: agent execution logs
- `schemas/`: structured-output contracts

`CLAIM_COVERAGE_CUTOVER_20260902.json` binds the exact historical frontier.
Prepared old receipts and prompts without a completed child revision are
preserved as evidence but are inert; a continuation creates a new versioned
receipt and prompt. The original capped schemas and receipt program also stay
byte-identical so completed lineage remains reproducible.

`audits/baseline_claim_only_v1/` preserves the first eight claim-level audits.
They were generated before target-coverage fields were added to the audit
contract, so they are supporting evidence only and cannot certify a `FULL`
label. Their original logs and states are preserved in matching legacy
subdirectories. Canonical audits in `audits/baseline/` use the strengthened
contract.

The source universe is the existing 24 FUN plus 7 Dagstuhl/TCS input manifests.
