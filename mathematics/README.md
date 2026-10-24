# Mathematical follow-ups

This directory supplies 28 unchanged Lean source files with selected
declarations and saved build evidence:

- `theorems/`: eight principal files for the cycle-coloring results, the Schur
  construction, and the three projective-cube families.
- `extensions/`: eight files covering square-root repair and exact failure,
  layered-density results, and further research counterexamples.
- `explanations/`: twelve files for the thirteen explanation packages; the
  square-root file under `extensions/` serves two entries in that census.
- `index.json`, `extensions/index.json`, and the adjacent receipts: theorem scope,
  source hashes, selected declarations, and recorded compiler results.

[supporting/](supporting/README.md) supplies seven additional archival formal
files cited in the appendices on the structural case studies and on the
further certified families, with saved compilation evidence.
[discoveries/](discoveries/README.md) supplies the twelve source-conjecture
deposit records, exact checkers and original model-audit evidence, cited in the
same two appendices.
Both have their own inventories and remain separate from the 312-source replay.

Replay all mathematical sources from the repository root:

```sh
python bugbank/lean/replay.py --group mathematics
```

See [the Lean replay instructions](../bugbank/lean/README.md) for dependency setup,
core-only replay, individual file selection, and axiom checking. Thirteen files
use Mathlib under Lean 4.30.0. The other fifteen use Lean's bundled libraries and
have recorded builds under both 4.30.0 and 4.34.0. Every imported project library
is supplied by those pinned environments; the shipped sources have no omitted
first-party Lean imports.

The indices preserve the connection between each formal statement and the
mathematical claim it supports. For example, the Schur optimum concerns the
specified two-threshold construction; the layered-density pullback assumes a
cube-free base; the larger-bag coloring results are combined with the source
conjecture's hypotheses in the written argument. The thirteen explanation
packages retain their defined cohort and individual repair scope.
