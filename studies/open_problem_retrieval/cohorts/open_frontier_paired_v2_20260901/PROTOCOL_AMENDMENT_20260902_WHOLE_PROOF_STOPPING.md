# Protocol amendment: whole-proof retrieval and first-solution stopping

Recorded: 2026-09-02

This amendment governs the continuation of the existing paired-v2 checkpoint.
It replaces the earlier six-item claim-inventory limit and the rule that made
an already-correct plain proof continue spending tokens to match BugBank. It
does not rewrite any completed model response, audit, receipt, or usage record.

## 1. Check the whole current proof against BugBank

The old baseline and revision schemas allowed at most six `results` entries.
The old retriever did query every entry it received, but the schema limit meant
that a seventh load-bearing claim could not be listed and therefore could not
be queried. This was especially problematic after a revision expanded a proof.

For every new draft:

- put every load-bearing claim or lemma in `results`, in proof order;
- include the complete proof sketch for each entry;
- impose no maximum number of entries; and
- for the BugBank arm, make one `k=3` query per entry using the exact claim,
  two newline characters, and that entry's exact proof sketch.

The receipt binds the full ordered inventory and the exact query derived from
each entry. A new claim or changed proof sketch is therefore covered by the
next BugBank pass. If the complete inventory cannot be represented within the
model context, the cell is incomplete; it must not silently omit later claims.

Historical capped prompts and receipts remain byte-for-byte unchanged. The
cutover manifest identifies them and the versioned files used for new work:
`CLAIM_COVERAGE_CUTOVER_20260902.json`.

## 2. Stop either arm at its first independently verified full solution

A solver's `FULL` label is not enough. An arm has a correct solution only when
its independent audit is complete, verifies every listed claim, confirms no
refutation, says the draft fully resolves the exact target, and says the
solver's resolution label is accurate.

At the first iteration satisfying all of those checks, stop that arm. Do not
require another confirmation call, an unchanged repeat of the proof, an empty
BugBank `acted_on_entry_ids` list, or additional tokens. This rule applies
equally to BugBank and plain.

If an arm never reaches a verified full solution, its old exact fixed-point
rule remains the basis for an inconclusive endpoint. An inconclusive BugBank
endpoint must have no acted-on records in its closing iteration. An
inconclusive plain endpoint must also reach the completed-call token total of
the BugBank endpoint. A stable partial plain arm may wait until that BugBank
target is known.

## 3. Count and compare tokens at the actual endpoints

For each arm, count valid completed revision and revision-audit calls through
its first verified full solution or valid inconclusive endpoint. Exclude the
shared baseline and baseline audit, failed or structurally invalid calls, and
calls made after the endpoint. Missing or nonnumeric usage is an error, not
zero.

After both arms have endpoints, record:

- the BugBank endpoint total;
- the plain endpoint total;
- `plain total - BugBank total`; and
- whether plain found a verified full solution with fewer tokens than BugBank.

Plain may therefore finish first and may legitimately use fewer tokens. While
the other arm remains unfinished, the comparison stays pending rather than
substituting zero.

Before this amendment, four BugBank arms continued after an iteration that is
now recognized as their first independently verified full solution. Those
completed artifacts are retained unchanged for auditability. The cutover
manifest seals them as historical surplus, and their tokens are not counted in
the first-solution endpoint totals. No new later-iteration receipt, prompt,
revision, audit, audit metadata, checker, or state may be created after an
arm's endpoint.
