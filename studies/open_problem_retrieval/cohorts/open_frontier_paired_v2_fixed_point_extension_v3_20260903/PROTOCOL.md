# Post-fixed-point paired extension protocol

This is a new experiment namespace. It does not reopen, append to, or rewrite
the original paired run. Each selected problem starts from immutable copies of
the original terminal proof and audit for each arm.

## Purpose

The original run stopped an inconclusive arm after an independently audited
exact proof-state fixed point. This extension tests whether additional,
predeclared search directions can move those fixed points.

## Sealed inputs

`EXTENSION_MANIFEST.json` binds every source input and, for each problem:

- `seeds/<record_id>/pair_terminal.json`, copied from the source run;
- `seeds/<record_id>/plain/revision.json` and `audit.json`;
- `seeds/<record_id>/bugbank/revision.json` and `audit.json`;
- each arm's auditable model-token total before the extension; and
- exactly three arm-neutral search lenses, in their scheduled order.

The seed files remain byte-for-byte immutable. Extension artifacts are written
only below the extension run root and its separate scratch/operations roots.

## Attempts

Both arms use `gpt-5.6-sol` with reasoning effort `max`. Every revision and
independent audit covers the complete ordered proof; there is no claim-count
cap. BugBank queries every complete `claim + "\n\n" + proof_sketch` and keeps
the first three results per claim.

Attempts 1, 2, and 3 use the three predeclared neutral lenses. The exact same
lens is shown to both arms on a given attempt. Unless an arm has already passed
the strict full-solution rule below, all three attempts must be completed and
independently audited. Attempts after 3 use a neutral exact-closure instruction
without an additional search lens.

The plain arm receives only the source, its own parent proof, that proof's
independent audit, and the scheduled neutral instruction. The BugBank arm also
receives the complete append-only retrieval receipt for its current parent.

## Stopping

The first audit that independently verifies every load-bearing claim and says
that the draft fully resolves the exact target stops that arm immediately. This
rule applies on every attempt, including attempts 1 and 2, and does not require
token matching.

Otherwise an arm cannot stop before three valid revision-and-audit attempts.
At attempt 3 or later, an inconclusive BugBank arm stops only when:

1. the proof state is byte-exact under canonical JSON to its immediate parent;
2. the audit reports no confirmed refutation or target/label mismatch;
3. no retrieved BugBank record was acted on in that attempt; and
4. all valid completed revision-and-audit call records through that endpoint
   attempt are auditable.

The plain arm has the same exact-closure and audit requirements. In addition,
its auditable extension-token total must be at least the BugBank arm's
extension-token total at BugBank's endpoint. Seed tokens do not count toward
this matching condition.

If an arm has no valid endpoint after 50 attempts, its result is
`INCOMPLETE_MAX_ATTEMPTS`. This is not a claim that no proof exists.

## Token reporting

Every terminal record reports both:

- incremental model tokens: valid completed revision and audit calls through
  the extension endpoint;
- lifetime model tokens: the sealed pre-extension total plus the incremental
  total.

Only incremental totals are used for the extension's plain-versus-BugBank
matching rule. Both totals must remain visible so the extension cannot erase
the cost of the earlier run. Failed, invalid, or partial operational retries do
not enter this predeclared stopping estimand or paired-token comparison. Their
raw append-only log bytes remain present for operational audit, but they are
not counted as valid completed endpoint calls.

## Runtime integrity

Execution requires a runtime seal binding the manifest, all seed/source files,
the exact runner, validator, retrieval code, BugBank database, model CLI, and
repository commit. The shared unattended batch wrapper, checkpoint helper, and
this extension's Slurm launcher are reviewed code and receive the same exact
commit-and-byte bindings. The seal also inventories the complete native Codex vendor
bundle, the Node and Python interpreters, SQLite, and an exact bubblewrap
execution profile. The manifest and seal used at launch must be byte-identical
to a commit reachable from local `origin/main`.

The Slurm launcher uses `--export=NIL`, fixes concurrency and other experiment
settings, and enters the batch through `env -i`. The batch again starts each
Python, Node, and checkpoint child from a sealed allowlist. Submission-shell
controls such as `BASH_ENV`, `NODE_OPTIONS`, and `PYTHONPATH` therefore cannot
change the reviewed runtime or its children.

Before any external operations or scratch namespace is created, opened for
mutation, or chmodded, the batch requires exactly one plain, non-symlink
package manifest and invokes only the corresponding fixed repository seal
utility. The successful seal must bind that manifest and the exact runner,
validator, and seal-utility paths. Namespace strings must be canonical and
their resolved paths are rechecked after creation and before `chmod`.

Each model call sees only its exact source, parent, audit when applicable, and
output schema. BugBank receipt text is embedded in the BugBank revision prompt;
the database itself is never mounted. The other arm, repository, host home, and
original run are not mounted. A fresh per-cell `/work` directory is reset to
empty under the canonical lock. User configuration and project rules are
ignored, shell snapshots and login shells are disabled, web search is disabled,
and a sealed inner permission profile denies model-tool network access and all
model-tool reads of the operational credential. Bubblewrap copies that credential
from inherited file descriptor 3 into the otherwise temporary Codex home; the
host credential path is never mounted, and descriptor 3 is consumed before the
model tool starts. The outer launcher receives an explicit environment allowlist
with no credentials, while the model-tool environment is reset to an explicit
safe set. Model and receipt bytes are first written outside
their canonical destinations, revalidated host-side, and atomically published
only if the final path is absent. Host-side temporary files for states, prompts,
metadata, terminals, and summaries also live in the private operational scratch
tree, outside the scientific run. A kill can therefore leave no unbound partial
temporary file inside the closed-world run; cross-filesystem publication fails
before changing the canonical target. The independent validator uses the same
outside-run discipline when atomically refreshing its one allowed report.
The sealed batch keeps any prior plain report present during validation so its
tampering remains visible, then requires the validator to publish a different
inode. Only `0:VALID_COMPLETE`, `1:VALID_INCOMPLETE`, and `2:INVALID` are valid
extension exit/report pairs; a missing, stale, or mismatched report prevents
launch and checkpoint.

`STOP_REQUESTED` is a graceful-drain boundary for scientific work. Once the
runner observes it, the runner may not admit a new retrieval, prompt, model
call, call-state record, or checker-producing audit. A cell that passed the
second STOP check while holding its canonical lock is already admitted and may
finish and publish its validated output. After the drain, the runner may still
write terminal records and stage summaries, and the independent validator may
refresh `VALIDATION_REPORT.json`; these contain only deterministic summaries of
already-existing evidence and do not start or expose a new scientific call.
Because the drain is checked at each stage boundary, a quiescent checkpoint may
end with one fully validated receipt or revision but no later stage from that
attempt. It may also contain the canonical RUNNING/failed state and log of one
interrupted call, with no canonical output. The independent validator reports
these exact, retryable trailing prefixes as valid but incomplete; it never
counts them as an audited attempt or scientific endpoint. Any skipped stage,
second partial attempt, malformed state, or output after an endpoint is invalid.
Cell locks and call states both bind the launcher PID and its Linux
process-start tick, so PID reuse cannot impersonate a surviving owner. While
holding descriptor 8, a new runner removes only an exactly bound lock whose
exact process is gone. If a
crash occurs between retiring that lock and publishing its replacement, a
retryable state may temporarily have no lock. If it occurs just after the
replacement lock is published, the strictly newer same-cell lock may not yet
match the older state's start time. These are valid-but-incomplete handoff
prefixes only: they count as no attempt, endpoint, or tokens. A missing,
same-cell, or strictly newer replacement lock is accepted only with the exact
canonical trailing state/log shape. A lockless RUNNING state or replacement
lock also requires the exact prior state owner to be gone; other lock
mismatches are invalid.

Before admitting a new cell, the runner removes the prior self-hashed
`INCOMPLETE` terminal snapshot. Thus an interruption can leave a missing
terminal, which is valid and can be reconstructed, but never a terminal that
claims to summarize an older prefix. It never removes a `COMPLETE` terminal.
Each call state also records the byte offset at which that call began appending
to its canonical log, a hash of all prior log bytes, and (when it ends) the
exact bytes from that offset through the end of the log by size and SHA-256.
This binds the retained raw history while model identity and token usage are
parsed only from the current call's segment. If a crash happened during output
publication, recovery promotes only already revalidated bytes and reconstructs
COMPLETE state only when the exact prompt/runtime lineage and that call's exact
model/token log segment agree. Until recovery finishes, the validator reports
the run as valid but operationally incomplete. If interruption lands while
checker files are being copied from an audit scratch directory, the validator
admits only the exact copied subset whose names, hashes, bytes, claim indices,
and scratch sources all agree. That subset remains operational evidence only;
the audit cannot count until complete metadata binds every required checker.

Every real runner invocation that can mutate the extension must inherit file
descriptor 8 and set `PAIRED_OPERATION_LOCK_FD=8`. Descriptor 8 must name the
plain file `<ops_root>/operation.lock`. Before any run-tree write, the runner
uses the sealed `flock` binary to acquire (or confirm) an exclusive nonblocking
lock on that shared open-file description, then proves that a separately opened
description cannot acquire it. The runner keeps descriptor 8 open for its whole
lifetime. Checkpoint/push automation must hold or inherit this same lock, so a
checkpoint cannot race a scientific write. Dry runs and the runner's read-only
`validate` stage are exempt.

The runner rejects the original run path and any extension manifest whose
operational directories overlap the repository, extension run, or original
experiment's operational directories. The independent validator replays every
BugBank query directly against the pinned read-only SQLite database,
reconstructs prompts, token totals, endpoints, and complete terminal payloads,
and rejects any unbound file, symlink, or noncanonical empty directory in the
run tree. Only exact directory names the sealed runner can create are allowed;
an empty canonical directory may remain from interruption between directory
creation and atomic file publication.
