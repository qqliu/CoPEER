# Whole-proof, first-solution paired protocol

Protocol ID: `WHOLE_PROOF_FIRST_SOLUTION_V1`

This protocol governs a fresh paired comparison between a plain
self-refinement arm and a BugBank-assisted arm. It has no historical cutover,
grandfathered artifact, or compatibility exception. A generic runner and an
independent validator must derive the run ID, roster, paths, hashes, model,
effort, and iteration ceiling from the sealed run configuration.

## 1. Freeze the scientific inputs before execution

The bootstrap manifest binds the ordered problem roster, exact target text,
authoritative source snapshots and extracted text, exact source locators and
excerpts, current-status search log, semantic audit, schemas, BugBank database,
model request, and isolated operations paths. The solver receives only the
bound six-field input JSON. It has no network access and does not receive the
status-search log, semantic audit, source-metadata URL fields, BugBank database,
other arm, or earlier experiment outputs. Verbatim canonical paper text is
deliberately supplied to both arms and may itself contain printed URLs. The
paired estimand is the effect of BugBank assistance conditional on this same
frozen full-paper context; it is not an estimate of solving without source
context.

No runtime call is allowed until a runtime seal binds the reviewed generic
runner, independent validator, feedback generator, native model-runtime bundle,
Node and Python/SQLite runtimes, bubblewrap and flock executables, repository
revision, exact BugBank bytes, operations namespace, shared unattended batch
wrapper, shared checkpoint helper, and run-specific Slurm launcher. All three
launch programs must exactly match the same recorded reviewed code commit as
the scientific runtime programs. The manifest and seal bytes must coexist at
the current `origin/main` tip. This Git check is
honest-checker self-attestation, not protection against a malicious Git server.
Preflight must validate both seals and the exact OS-isolation contract.

The run-specific Slurm launcher uses `--export=NIL`, fixes every experiment
parameter (including concurrency), and starts the batch wrapper through
`env -i` with an exact safe environment. Submission-shell values such as
`BASH_ENV`, `NODE_OPTIONS`, `NODE_PATH`, `PYTHONPATH`, and Python user-site
controls are not admitted. The batch wrapper likewise launches every sealed
Python and Node process from an exact allowlist rather than inheriting its
ambient environment.

External namespace mutation follows authentication. The batch first requires
exactly one plain, non-symlink package manifest, selects the corresponding
fixed repository seal utility, and completes the runtime-seal check. It then
requires the seal's manifest, runner, validator, and seal-utility paths to
equal the requested paths. Canonical operations and scratch paths are checked
before creation and resolved again before their permissions may change.

Every mutating runner invocation must inherit file descriptor 8 (FD 8) for the plain
regular file `<ops_root>/operation.lock` and set
`PAIRED_OPERATION_LOCK_FD=8`. It must acquire a nonblocking exclusive flock on
that shared open-file description, prove that a separately opened description
is excluded, and recheck the path, descriptor, device, and inode before every
admission or publication. Replacing the lock pathname must fail closed. Dry-run
and read-only validation are the only exemptions.

## 2. Use one neutral baseline for both arms

For each problem, make exactly one neutral baseline proof and one independent
audit of that proof. The solver-facing baseline prompt and schema, and the
solver-facing baseline-audit prompt and schema, contain no arm, pairing,
treatment, receipt, retrieval, or BugBank vocabulary. The wrapper adds only
fixed lineage fields after the auditor responds. Fork the exact audited
baseline into `bugbank` and `plain`; do not generate a separate baseline for
either arm.

Every draft represents its whole current proof as a nonempty ordered `results`
array. It must include every load-bearing claim or lemma in proof order, with
that claim's complete `proof_sketch`. There is no claim-count cap. A response
that omits later claims because of a context or output limit is incomplete and
cannot be accepted as a valid draft.

## 3. Keep the treatment contrast causally isolated

At each BugBank iteration, mechanically query every `results` row in the exact
current parent proof. The query text is exactly:

```text
<claim>\n\n<proof_sketch>
```

Use `k=3` against the sealed database, with the sealed deterministic retrieval
configuration. The receipt must bind the parent proof, complete ordered query
inventory, exact query text and returned records. Expose the complete receipt
and the preceding independent audit to the BugBank revision call. Require the
revision to list every used hit in `acted_on_entry_ids` and give a specific
reason for every unused hit.

The plain revision receives the same exact parent proof and preceding audit,
but no BugBank receipt, hit, entry ID, text, placeholder, summary, or indirect
derivative. Its solver-facing schema also omits treatment bookkeeping; the
wrapper adds the fixed empty plain-lineage fields afterward. A plain artifact
must never depend on a BugBank artifact. Both arms use the same sealed model
and reasoning effort.

Independently audit every baseline and revision against the exact frozen input.
The audit must check every listed claim and proof step, target coverage, the
claimed resolution, constructions or counterexamples, and executable evidence
where applicable. The independent auditor must not trust the solver's label or
a retrieved BugBank record. Checker source and results must be preserved and
bound when a checker is used.

## 4. Stop either arm at its first strictly verified full solution

An arm has a verified full solution at iteration `i` exactly when its valid,
complete independent audit at `i` satisfies all of the following:

- the draft's `claimed_resolution` is `FULL`;
- the audit covers the complete ordered `results` inventory one-for-one;
- every audited claim has verdict `VERIFIED`;
- `confirmed_refutations` is empty;
- `target_verdict` is `FULLY_RESOLVES_TARGET`;
- `claimed_resolution_verdict` is `ACCURATE`; and
- `overall` is `VERIFIED`.

The first iteration satisfying this predicate is the arm's endpoint. Stop the
arm immediately. Do not require a second confirmation, an unchanged proof,
an empty `acted_on_entry_ids` array, budget matching, or any other call. This
rule is identical for BugBank and plain. A scheduler may interleave problems
and arms in any order, but it may not change either arm's logical endpoint.

Once an arm has an endpoint, no later receipt, retrieval, prompt, revision,
audit, audit metadata, checker, usage state, or recovery artifact may be made
for that arm.

A stop/drain request is checked once before attempting a scientific cell and a
second time after acquiring that cell's exclusive lock, before publishing a
prompt, clearing scratch, writing call state or log, or starting a subprocess.
If either check sees `STOP_REQUESTED`, the lock is removed and that cell creates
no scientific artifact. A cell that passed the second, under-lock check is
already admitted and may finish and publish after the stop file appears; this
is an in-flight completion, not a new call. Deterministic terminal records,
summaries, and the derived validation snapshot may be rebuilt after drain, but
they may not cause retrieval or model work.

At that same admission boundary, the runner removes any earlier self-hashed
`INCOMPLETE` pair-terminal snapshot for the selected record. Therefore a crash
after new scientific progress can leave the derived terminal missing, but
cannot leave an older incomplete snapshot that falsely describes the newer
endpoint. A `COMPLETE` or malformed terminal is never removed this way.

After SIGKILL or host loss, an exact RUNNING/FAILED prefix is valid incomplete
evidence, never endpoint evidence. RUNNING normally has its exact canonical
cell lock. Two narrower retry crash windows are also incomplete: the old exact
RUNNING owner is proved dead and its lock is either absent after stale-lock
unlink, or replaced by a new exact sealed lock before RUNNING refresh. Under
the same operation gate, the runner may resume these prefixes. If an already
validated output was atomically published just before interruption, it may
reconstruct the COMPLETE state only from the exact old RUNNING admission,
dead PID/starttime, canonical call log, sealed telemetry, and finalized output
binding. Malformed or unbound prefixes fail closed.

All host-side publication temporaries—for call states, prompt and audit
metadata, model outputs, receipts, terminals, summaries, and the derived
validation report—must be created in the private external scratch root, never
next to a canonical file inside the closed-world run. The runner verifies
before its first in-run mutation that scratch is a plain private directory on
the same filesystem as the run. It fsyncs each complete temporary and then
uses an atomic rename for replaceable records or an atomic hard link for
publish-if-absent records. Thus an interruption may leave an ignored private
scratch file, but cannot leave an unexplained partial file in the run tree.

## 5. Inconclusive endpoints use the exact fixed-point rule

If a valid audit does not verify a full solution, define the proof state as the
exact JSON value of these three fields:

- `claimed_resolution`;
- the complete ordered `results` array of `{claim, proof_sketch}` objects; and
- `final_writeup`.

Semantic similarity or an unchanged claim list is not equality. A BugBank arm
may stop inconclusively only when its independently audited revision has exact
proof-state equality with its parent, its closing `acted_on_entry_ids` is
empty, and the audit is settled with no confirmed refutation or overclaim. If
the proof changes, the audit finds a defect, or any BugBank hit is acted on,
the next BugBank iteration must retrieve again over the complete new proof.

A plain arm that has not found a verified full solution may stop
inconclusively only when it has the same independently audited exact
proof-state fixed point and its auditable completed-call token total is at
least the BugBank endpoint total. A stable plain arm may wait without making a
model call until the BugBank endpoint and token total are known. If BugBank is
unfinished, zero or a partial BugBank total must never be substituted.

The configured maximum iteration is an operational safety ceiling, not a
scientific endpoint. Reaching it without a valid solved or inconclusive
endpoint leaves the arm incomplete and requires review; it does not make the
arm terminal.

## 6. Count tokens only from valid endpoint calls

For an arm, its token total is the sum recorded for valid completed revision
and revision-audit calls from iteration 1 through its endpoint, inclusive.
Each counted state must have the exact run ID, record ID, arm, iteration,
stage, sealed model, and sealed reasoning effort and must have a valid
nonnumeric-free usage record. Accepted completion states must be enumerated by
the runtime seal; recovered completion is acceptable only when all the same
identity, execution, artifact, and usage bindings are present and valid.
Before each call, RUNNING records the byte offset at which that call starts in
its canonical append-only log and the SHA-256 of all bytes before that offset.
Every COMPLETE, FAILED, SPAWN_FAILED, or RECOVERED_COMPLETE state preserves
that prefix hash and binds the exact suffix from the offset through the current
end of the log by canonical path, offset, byte length, and SHA-256.
Token, model, and reasoning-effort telemetry must be parsed only from that
bound suffix; telemetry from an earlier failed attempt never counts for a
later retry.

Do not count the shared baseline, baseline audit, retrieval, failed or invalid
calls, partial state, calls belonging to another cell, or post-endpoint calls.
Missing or nonnumeric usage fails closed; it is not zero. The terminal record
must store both endpoint totals, `plain - BugBank`, and whether plain reached a
verified full solution using fewer tokens than BugBank. Comparison fields stay
pending until both endpoints and both totals are valid.

## 7. Validate independently and fail closed

The validator must recompute endpoints from immutable drafts, audits,
receipts, prompt metadata, checker artifacts, and exact completed-call state;
it must not accept a terminal record as authority for itself. It must reject:

- missing, duplicate, unexpected, cross-record, cross-arm, or cross-iteration
  artifacts;
- any capped or incomplete whole-proof inventory or BugBank receipt;
- treatment leakage into the neutral baseline or plain arm;
- any runtime artifact after an arm's endpoint;
- token states with wrong identity, model, effort, status, or usage;
- inconclusive plain endpoints below the matched BugBank budget;
- a roster, input, source, schema, database, runtime, or operations binding
  that differs from its seal; and
- any historical-cutover or grandfathering field in this fresh run.

The whole run tree is closed world: every entry must be an expected real
directory or regular file; symlinks, FIFOs, sockets, devices, and unexplained
empty directories are invalid. The sole optional unbound file is exactly
`VALIDATION_REPORT.json`, a self-hashed, non-authoritative derived snapshot.
The validator must never use that snapshot as scientific evidence and may
atomically refresh it after each checkpoint using the same external-scratch
publication rule.

The sealed batch preserves any prior plain snapshot while validation runs, so
the validator can detect tampering, and then requires publication on a new
inode. It accepts only the hard-run exit/report pairs `0:VALID_COMPLETE`,
`1:INCOMPLETE`, and `2:INVALID`. Absence, inode reuse, or any other pairing
fails closed before launch or checkpoint.

The experiment is complete only when both arms of every problem have valid
endpoints and every pair has an auditable token comparison. An inconclusive
endpoint is a stable failure to solve, not a solution.
