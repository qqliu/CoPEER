# Protocol amendment: treated-proof closure

Recorded: 2026-09-02 11:17:37 EDT

Historical note: the later whole-proof and first-solution rules in
`PROTOCOL_AMENDMENT_20260902_WHOLE_PROOF_STOPPING.md` supersede the operational
stopping and retrieval rules below. This file is retained to document the
earlier checkpoint decisions.

## Reason

The original terminal test treated an unchanged ordered claim list plus a
settled independent audit as a fixed point. That test allowed a BugBank arm to
close in the same iteration in which it acted on retrieved records, even when
the proof sketches had been revised. `tcs_count_graphs_vc_at_most_k` exposed
the problem: its iteration-1 BugBank revision acted on three records and
hardened several proofs, but retained the five exact claim strings and was
therefore recorded as terminal.

This did not provide the requested closure pass over the revised treated
proof. The terminal rule was first corrected prospectively and retroactively
for all 31 pairs, then strengthened further the same day as described below.

## Intermediate correction (now superseded)

At the intermediate correction, a BugBank revision with a nonempty
`acted_on_entry_ids` list was never terminal in that iteration. The resulting
revision became the parent of a fresh BugBank receipt, revision, and
independent audit in the next iteration. That intermediate rule retained the
then-current cap of ten iterations; the superseding rule below removes that
scientific stopping condition.

Existing BugBank terminal snapshots that closed on a nonempty acted-on list
are invalidated and reopened. Plain-arm terminal states remain unchanged. The
model (`gpt-5.6-sol`, maximum reasoning), retrieval depth (`k=3` per claim),
all-status/no-exclusion corpus, audit requirements, and iteration cap are
unchanged.

## Superseded matched-refinement rule (historical)

The user subsequently required every newly produced proof—not only revisions
with a nonempty acted-on list—to receive another BugBank pass. Closure now
compares the complete proof state (`claimed_resolution`, full `results`, and
`final_writeup`) rather than only exact claim strings. The plain arm is also
reopened as needed and must perform native self-refinement through a stable,
audited proof state while consuming at least the terminal BugBank arm's
recorded model-token total. Whole-cycle overshoot is explicitly allowed and
reported. The controller processes BugBank first so the plain target is known.

The former ten-iteration scientific cap is superseded. Fifty is used as an
operational controller/schema ceiling; reaching it unfinished requires an
extension and resume rather than a terminal classification. Terminal closure
also requires complete, numeric revision-and-audit token telemetry for every
cycle through the terminal iteration, so the plain arm's matched target is
auditable.

## Retrieval interpretation

The original draft prompt and schema allowed at most six recorded claims. The
receipt program queried every row it received, but that capped inventory could
omit later load-bearing claims after a proof expanded. Completed receipts made
under that rule remain sealed rather than being rewritten.

Prospectively, every load-bearing claim is recorded and queried; there is no
claim-count cap. Each query contains the exact claim statement, two newlines,
and its exact proof sketch. The receipt binds the complete ordered claim list,
each proof-sketch hash, and each query-text hash. Thus a changed proof sketch
changes the bound query even when the claim sentence is unchanged, and a newly
added claim is included in the next BugBank pass.

The versioned receipt program and schemas apply only to new work. Prepared old
receipts and prompt metadata that had no completed revision at the cutover are
preserved but inert. The exact boundary, historical bindings, and first-FULL
surplus allowlist are recorded in
`CLAIM_COVERAGE_CUTOVER_20260902.json`.
