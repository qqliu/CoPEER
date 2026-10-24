# Restart handoff: stopped paired open-frontier run

Checkpoint time: 2026-09-02, approximately 12:00 EDT

Historical checkpoint note: this document records the state and operating rule
at the midday migration boundary. The continuation now follows
`PROTOCOL_AMENDMENT_20260902_WHOLE_PROOF_STOPPING.md`: all load-bearing claims
are covered with no six-item cap, and either arm stops at its first strictly
audited full solution. Use the current resume script and validator rather than
the obsolete BugBank-first/token-matching steps below.

This run was stopped at the user's request because the current server has too
few cores. This is a restartable checkpoint, not a final experiment result.
No solver, audit, retriever, or controller process remains alive, and
`locks/` is empty.

## Current validated state

The independent checkpoint validator reports `INCOMPLETE`, with **0 invalid
findings**, 84 expected incomplete findings, and 0 warnings. Its complete
machine-readable snapshot is `validation_report.json`.

- input universe: 31/31 valid;
- arm-neutral baselines: 31/31 valid;
- target-aware baseline audits: 30/31 valid;
- BugBank receipts: 49/49 present receipts valid;
- revisions: 41/41 present BugBank and 35/35 present plain revisions valid;
- revision audits: 34/34 present in each arm valid;
- terminal arms: 8 BugBank and 1 plain;
- complete pair terminals: 1/31.

The one complete pair is `fun2026_magazine_marking_rounds`. Both arms reach an
audited **inconclusive partial fixed point**, not a full solution. Its BugBank
arm used 182,873 completed-call tokens; its plain arm used 195,418, meeting the
target with 12,545 tokens of permitted whole-cycle overshoot.

The eight terminal BugBank arms are:

- `fun2026_level3_additive_restoration`, iteration 2, inconclusive fixed point,
  307,679 tokens;
- `fun2026_magazine_marking_rounds`, iteration 1, inconclusive fixed point,
  182,873 tokens;
- `fun2026_wst_log_worstcase_updates`, iteration 2, inconclusive fixed point,
  226,522 tokens;
- `fun2026_zombie_high_dimensional_grid`, iteration 1, verified full,
  146,004 tokens;
- `tcs_incremental_toposort_nsqrtm`, iteration 2, inconclusive fixed point,
  376,040 tokens;
- `tcs_karp_rabin_collision_detection`, iteration 1, inconclusive fixed point,
  162,385 tokens;
- `tcs_directed_cycle_above_min_outdegree`, iteration 1, inconclusive fixed
  point, 187,769 tokens;
- `tcs_k6_minus_edge_induced_minor`, iteration 1, inconclusive fixed point,
  263,285 tokens.

Do not report eight solved problems. Only the zombie BugBank arm currently has
a verified-full classification, and its plain mate has not yet met the paired
protocol. The strengthened closure and token-matching rule reopened results
that older terminal snapshots had called complete.

The validator sees 20,798,476 tokens in 218 execution logs with final token
counts. Canonical structured arm-state totals are 7,528,070 BugBank tokens and
4,501,050 plain tokens. Those broad telemetry totals include 341,001 BugBank
and 62,441 plain tokens from failed calls, as well as completed states outside
a terminal contiguous chain. Failed calls do not count toward arm matching.
The shared baseline and baseline-audit calls are also excluded from matching.
No USD cost was recorded.

## Superseded protocol at this historical checkpoint

There are 24 FUN targets and 7 Dagstuhl/TCS targets. Every target starts from
one shared arm-neutral baseline and its independent audit. The same baseline
then forks into:

- `bugbank`: a fresh deterministic `k=3` receipt is generated from every exact
  parent claim and exposed in full to the revision agent;
- `plain`: native self-refinement and the same kind of independent audit, with
  no BugBank receipt, retrieval, placeholder, or text exposure.

Both arms use `gpt-5.6-sol` at maximum reasoning effort. Do not substitute a
faster model. The BugBank database, retrieval depth, source universe, and
prompt isolation are pinned and validated.

The current user-requested iteration rule is:

1. Finish BugBank first for each problem.
2. Every materially new BugBank proof becomes the parent of a fresh
   receipt/revision/audit cycle. A nonempty `acted_on_entry_ids` also forces a
   new cycle.
3. BugBank stops only when the exact proof state is unchanged, the fresh audit
   is settled, and `acted_on_entry_ids` is empty. Proof state means
   `claimed_resolution`, every ordered `{claim, proof_sketch}` pair, and
   `final_writeup`.
4. Then continue plain native self-refinement through a settled, exact proof
   fixed point until its cumulative completed revision-plus-audit tokens are
   **at least** the terminal BugBank total. Overshoot is explicitly allowed.
5. Fifty iterations is an operational controller/schema ceiling, not a
   scientific stopping rule. If a still-open arm reaches it, version and raise
   the runner constant, CLI guard, audit/revision schemas, and validator bound
   together, review that mechanical change, and resume. Do not classify the
   cap as a result.

The runner freezes the first valid terminal iteration. The validator now walks
iterations in order, uses that same first-terminal rule, and rejects later
same-arm receipts, prompts, revisions, audits, and audit metadata as outside
the frozen protocol. It also rejects an audit whose
`claimed_resolution_verdict` contradicts the rank implied by the parent's
`claimed_resolution` and the audit's `target_verdict`.

## Exact per-problem continuation point

In the table, `r/a N` means a valid completed revision and audit at iteration
N; `receipt N` means the next BugBank receipt already exists; `IFP` means an
audited inconclusive fixed point; and `FULL` means an audited verified-full
fixed point. Token values count only contiguous, independently valid completed
revision/audit cycles. `wait` means the runner intentionally holds plain until
that problem's BugBank arm is terminal.

| Problem | BugBank checkpoint and exact next step | Plain checkpoint and next step | Valid-cycle tokens B / P |
|---|---|---|---:|
| `fun2026_max_bounded_sums_integer_linear` | r/a 1; generate receipt 2 | r/a 1; wait, then revision 2 | 211,113 / 91,302 |
| `fun2026_tiles_no_teleport_general` | r/a 1; generate receipt 2 | r/a 1; wait, then revision 2 | 206,154 / 114,029 |
| `fun2026_recursive_maze_linear` | revision 1; retry audit 1 | r/a 1; wait, then revision 2 | — / 145,920 |
| `fun2026_torus_push_tight_bounds` | r/a 1 + receipt 2; retry revision 2 | r/a 1; wait, then retry revision 2 | 223,871 / 268,457 |
| `fun2026_level3_additive_restoration` | terminal IFP at 2 | r/a 2; retry revision 3 | 307,679 / 263,189 |
| `fun2026_berlin_safe_house_better_than_two` | r/a 1; generate receipt 2 | r/a 1; wait, then revision 2 | 217,945 / 137,464 |
| `fun2026_careless_coupon_tight_hitting` | r/a 2 + receipt 3; retry revision 3 | r/a 1; wait, then revision 2 | 439,798 / 156,889 |
| `fun2026_magazine_marking_rounds` | terminal IFP at 1 | terminal IFP at 1; pair complete | 182,873 / 195,418 |
| `fun2026_optimized_magazine_steps` | r/a 2 + receipt 3; retry revision 3 | r/a 2; wait, then revision 3 | 515,304 / 269,369 |
| `fun2026_pack_a9_in_a0` | r/a 1; generate receipt 2 | r/a 1; wait, then revision 2 | 182,086 / 88,402 |
| `fun2026_pack_a10_in_a1` | revision 2 exists; run audit 2 | r/a 1; wait, then revision 2 | 115,564 / 89,447 |
| `fun2026_pack_a9_in_a1` | r/a 1 + receipt 2; retry revision 2 | r/a 1; wait, then revision 2 | 148,617 / 115,275 |
| `fun2026_arrival_constant_level_width` | r/a 1; generate receipt 2 | r/a 1; wait, then revision 2 | 175,255 / 128,396 |
| `fun2026_swish_29_cards` | r/a 1; generate receipt 2 | r/a 1; wait, then revision 2 | 186,513 / 112,121 |
| `fun2026_fitting_hexasort_constant_threshold` | r/a 2 + receipt 3; retry revision 3 | r/a 1; wait, then revision 2 | 434,054 / 134,780 |
| `fun2026_wst_log_worstcase_updates` | terminal IFP at 2 | r/a 2; revision 3 | 226,522 / 205,873 |
| `fun2026_zombie_high_dimensional_grid` | terminal FULL at 1 | r/a 1; revision 2 | 146,004 / 75,290 |
| `fun2026_unrotatable_domino_survival` | r/a 1; generate receipt 2 | r/a 2; wait, then retry revision 3 | 196,522 / 241,998 |
| `fun2026_token_number_half_bound` | r/a 1; generate receipt 2 | r/a 1; wait, then revision 2 | 135,377 / 146,286 |
| `fun2026_planar_nemesis_fixed_exits` | r/a 1 + receipt 2; retry revision 2 | r/a 1; wait, then revision 2 | 211,385 / 123,885 |
| `fun2026_batdroid_fewer_than_77_shades` | revision 1 preserved; replay audit 1 | revision 1 preserved; wait, then replay audit 1 | — / — |
| `fun2026_fog_chess_queen_win_within_50` | baseline exists; retry baseline audit | baseline exists; wait for baseline audit | 0 / 0 |
| `fun2026_mms_simultaneous_l_r_enumeration` | r/a 2 + receipt 3; retry revision 3 | r/a 1; wait, then revision 2 | 414,668 / 146,343 |
| `fun2026_happy_vertex_cographs` | revision 1; retry audit 1 | r/a 1; wait, then revision 2 | — / 165,466 |
| `tcs_incremental_toposort_nsqrtm` | terminal IFP at 2 | r/a 2; revision 3 | 376,040 / 262,730 |
| `tcs_karp_rabin_collision_detection` | terminal IFP at 1 | r/a 1; revision 2 | 162,385 / 97,500 |
| `tcs_count_graphs_vc_at_most_k` | revision 2 exists; retry audit 2 | r/a 1; wait, then revision 2 | 173,141 / 106,989 |
| `tcs_directed_cycle_above_min_outdegree` | terminal IFP at 1 | r/a 1; revision 2 | 187,769 / 100,899 |
| `tcs_h3_free_induced_disjoint_paths` | revision 2 exists; retry audit 2 | r/a 1; wait, then revision 2 | 204,136 / 126,501 |
| `tcs_p8_free_bipartite_fvs` | revision 2 exists; retry audit 2 | r/a 1; wait, then revision 2 | 186,859 / 116,134 |
| `tcs_k6_minus_edge_induced_minor` | terminal IFP at 1 | r/a 1; revision 2 | 263,285 / 124,988 |

The exact source of truth is still `validation_report.json` plus the canonical
artifacts, not this human-readable table. The runner validates and skips every
sound immutable artifact, so it will resume at these boundaries without
repeating completed calls.

## Interrupted work and forensic recovery

All active controllers were stopped, their full process trees were checked
dead, and every canonical lock was removed only after preserving the exact
interrupted evidence.

- PID 94074 / session 55512: torus plain and BugBank iteration-2 revisions.
- PID 118038 / session 69002: Batdroid BugBank/plain iteration-3 and
  unrotatable plain iteration-3 revisions.
- PID 162819 / session 58996: careless, fitting, and M&M BugBank iteration-3
  revisions.
- PID 199268 / session 5057: A9-in-A1 and planar-nemesis BugBank iteration-2
  revisions. A10-in-A1 BugBank revision 2 completed before the stop and remains
  canonical.
- PID 197509 / session 80439: Count-Graphs, H3, and P8 BugBank iteration-2
  audits.
- PID 199477 / session 69970: Level-3 plain iteration-3 revision.
- PID 199487 / session 86465: optimized-magazine BugBank iteration-3 revision.
- PID 104574 / session 97392: Fog baseline audit.

The ten interrupted revision locks owned by PIDs 94074, 118038, 162819, and
199268 have individual recovery records under `recoveries/revisions/` and
byte-for-byte state/lock/log copies under
`forensics/revision_recovery_pids_94074_118038_162819_199268/`. Their canonical
states say `READY_FOR_RELAUNCH`.

The three interrupted TCS audits are archived under
`forensics/audit_recovery_pid_197509/`; its manifest SHA-256 is
`0b8982b08ecef7fcbfbb589af31b7b17e146c76fc185f7d993f8378aaf6e6cee`.
It includes the Count and P8 scratch checker sources and records that H3's
scratch directory was empty.

The Fog, Level-3, and optimized-magazine interrupted cells are archived under
`forensics/stop_checkpoint_20260902T154455Z/`; the manifest SHA-256 is
`45eb905664392447e0fb835349c1a2ddc99e798b3915f35be83806de72367b72`.
Their failed-call telemetry is preserved: Fog audit 150,814 tokens, Level-3
plain revision 62,441, and optimized BugBank revision 130,889. These calls did
not produce valid canonical outputs and are excluded from completed-cycle
matching.

Three orphan audit temporaries were archived and removed from canonical output
paths. The manifest is
`forensics/orphan_audit_temporaries_20260902/recovery_manifest.json`, SHA-256
`3f88bfb536db276bff1c5383efe7c54417520495c2959002b46264a650517d80`.
Arrival's temporary had already been superseded by a valid final audit; Happy
and recursive-maze failed strict validation and must retry their audits.

Four Batdroid audits said `ACCURATE` even though a parent labeled `NONE` was
judged to contain `VALID_PARTIAL_PROGRESS`; the protocol-derived label is
`UNDERSTATED`. The model outputs were not edited. The four audits and every
descendant bound to their hashes were archived byte-for-byte, then removed
from canonical paths so replay begins at both iteration-1 audits. The manifest
is `forensics/batdroid_semantic_invalidation_20260902/quarantine_manifest.json`,
SHA-256
`0b04c906a48ff5b5a078e0194e7099e9c53e8de39e6f15d91c79426df1f861d7`.
Both iteration-1 revisions and the reusable BugBank receipts through iteration
2 remain canonical.

Other failed canonical cells that will be retried automatically are
Happy BugBank audit 1 (93,073 tokens) and recursive-maze BugBank audit 1
(117,039 tokens). Interrupted or failed calls are incurred telemetry, but only
complete, valid revision-plus-audit states count toward the matched-arm token
rule.

For the optimized-magazine result, retain the audit nuance: claim 2 refutes the
supplied ordinary-transition derivation. It is not a mathematical refutation
of the requested `Omega(n^(3/2))` proposition.

## New-server prerequisites

**Path binding is mandatory.** Resume from the exact physical repository root
`<mount-root><machine-root>/anonymous-user/new/proof-verification`. Persisted prompt
and audit metadata embed this absolute path, and the launcher refuses a
relocated checkout. If the replacement server cannot expose that path, do not
launch the checkpoint until an explicit metadata migration has been designed
and independently reviewed.

The standalone English instructions for a Fable operator are
`qedbench_certificate_availability_triage/FABLE_OPEN_PROBLEM_PAIRED_PROTOCOL.md`.
They distinguish resuming this model-pinned campaign from running a separate
Fable-as-solver replication.

The parent repository was on branch `main` at
`a0cc9ec2adbc490214baa564a2ae8557de26f875` before this stop-checkpoint commit.
Use the commit containing this handoff (`git log -1 --oneline`) after the push.

`BugBank` is a nested Git checkout recorded as a gitlink but has no usable
root `.gitmodules` mapping. Its repository URL is
`[contact removed]:annacgilbert/BugBank.git`. On a fresh server, make sure
`BugBank/` is checked out separately at:

```text
d761df6dce23012ad51e00aba3667d9b3f0dd79a
```

Its required database SHA-256 is:

```text
a2b312e1e601d0f53c6a363530d9cf89462b92869dc63b28073537ac294ec15a  BugBank/bugbank.sqlite
```

The stopped server used `codex-cli 0.152.1`, Node `v25.8.2`, and Python
`3.14.4`. The replacement needs an authenticated `codex` executable with
access to the requested model, plus `node`, `python3`, `jq`, `xargs`, and
`sha256sum`. Exact CLI version equality is not part of the scientific
treatment, but the requested model and reasoning settings are fixed in the
runner and must remain `gpt-5.6-sol` / `max`.

Normal execution transcripts under `logs/` are ignored by the root Git policy.
They are not required to resume: completed-call token totals and lineage live
in committed state JSON, and durable audit checker copies live under
`checkers/`. Stop-specific forensic transcripts are included in this
checkpoint. Scratch paths under `/tmp/open_frontier_paired_v2/` are disposable;
do not copy them to the new server as active state.

## Historical restart commands (superseded)

After pulling the checkpoint commit at the exact bound path and restoring the
nested BugBank checkout, run from the root of this repository:

```bash
git switch main
git pull --ff-only origin main
if [[ ! -d BugBank/.git ]]; then
  git clone [contact removed]:annacgilbert/BugBank.git BugBank
fi
git -C BugBank fetch origin
git -C BugBank switch --detach d761df6dce23012ad51e00aba3667d9b3f0dd79a
git status --short --branch
git -C BugBank rev-parse HEAD
sha256sum BugBank/bugbank.sqlite
find qedbench_certificate_availability_triage/runs/open_frontier_paired_v2_20260901/locks -maxdepth 1 -type f -print
node --check qedbench_certificate_availability_triage/scripts/open_frontier_paired_v2_runner.mjs
bash -n qedbench_certificate_availability_triage/scripts/resume_open_frontier_paired_v2.sh
python3 -m py_compile qedbench_certificate_availability_triage/scripts/validate_open_frontier_paired_v2.py
python3 qedbench_certificate_availability_triage/scripts/validate_open_frontier_paired_v2.py \
  --allow-incomplete \
  --report qedbench_certificate_availability_triage/runs/open_frontier_paired_v2_20260901/validation_report.json
```

The last command should report `INCOMPLETE`, 0 invalid findings, 31/31 inputs,
31/31 baselines, 30/31 baseline audits, and 1/31 valid pair terminals before
new work starts. If it reports `INVALID`, stop and resolve that structural
failure; do not launch agents against an invalid checkpoint.

Then use the included isolated-controller launcher. `PAIR_JOBS` is the number
of different problems processed simultaneously. Each problem controller uses
one model call at a time and enforces BugBank-first sequencing internally.
For example:

```bash
PAIR_JOBS=16 qedbench_certificate_availability_triage/scripts/resume_open_frontier_paired_v2.sh
```

Choose `PAIR_JOBS` to fit the new server and API concurrency quota. One
controller per problem avoids a failed or long BugBank arm blocking unrelated
plain arms. The script refuses to start if any canonical lock exists, verifies
the pinned database and checkpoint first, and runs all 31 IDs as isolated
controllers. Valid artifacts are skipped. If a transient model call fails,
rerun the same command; it resumes the failed cell and skips everything valid.

For a single-problem manual retry, use:

```bash
node qedbench_certificate_availability_triage/scripts/open_frontier_paired_v2_runner.mjs \
  --stage all \
  --only tcs_count_graphs_vc_at_most_k \
  --concurrency 1 \
  --max-iterations 50
```

Do not run the same problem ID in two controllers. Different IDs are safe to
run in parallel. Never delete a lock merely because a job appears slow. After
a crash, first prove the owning PID and all exact-scratch children are dead,
archive the lock/state/log/temp/checker evidence with hashes, and only then
mark the cell ready for relaunch, following the recovery manifests above.

At any checkpoint, materialize terminal snapshots and validate with:

```bash
node qedbench_certificate_availability_triage/scripts/open_frontier_paired_v2_runner.mjs \
  --stage terminal --concurrency 16 --max-iterations 50
python3 qedbench_certificate_availability_triage/scripts/validate_open_frontier_paired_v2.py \
  --allow-incomplete \
  --report qedbench_certificate_availability_triage/runs/open_frontier_paired_v2_20260901/validation_report.json
```

For the final gate, omit `--allow-incomplete`. Completion requires validator
status `VALID_COMPLETE`, 0 invalid and 0 incomplete diagnostics, and 31/31
valid pair terminals. Do not turn an inconclusive fixed point into a claimed
solution; final mathematical outcomes come from each independently audited
terminal record.
