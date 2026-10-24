# Hypothesis-generating BugBank-targeted stress test (never pool with confirmatory or outcome-blind cohorts)

Run ID: `open_frontier_paired_targeted_stress_v2_20260904`

This is a fresh, isolated paired open-problem package with 6
records. It contains no model results. `RUN_MANIFEST.json` binds the ordered
roster, normalized targets, verbatim source passages, frozen authoritative
source snapshots, schemas, protocol, model request, BugBank database hash, and
separate operations paths. Both arms receive the same frozen full canonical
paper text. The paired estimand is the effect of BugBank assistance conditional
on that symmetric source context. Verbatim paper text may contain printed URLs;
separate source-metadata URL fields are not solver inputs.

Launch is intentionally blocked. Before any model call, implement and review a
generic config-driven runner and independent validator, create a separate
`RUNTIME_SEAL.json` binding their exact bytes and execution environment, and
make preflight require both seals. Do not point the historical paired-v2 runner
or validator at this directory.
