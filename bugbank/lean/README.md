# Lean certificates and replay

This directory contains the 284 corpus certificates, the selected declarations
and their recorded axiom audits, and a reproducible Lean environment. The replay
driver also covers the 28 mathematical follow-up files in `../mathematics/`.
It preserves the original proof files and checks the 407 selected declarations
in disposable copies.
The inventory covers `bugbank/certificates/`, `mathematics/theorems/`, and
`mathematics/extensions/`. Additional archival sources and their saved checks are
indexed separately in [mathematics/supporting](../../mathematics/supporting/README.md).

## Requirements and preparation

Install [Elan](https://github.com/leanprover/elan), Python 3.9 or newer, and Git.
The main environment uses Lean **4.30.0** and Mathlib commit
`c5ea00351c28e24afc9f0f84379aa41082b1188f`. The existing `lake-manifest.json`
pins all transitive packages. Run these commands from the repository root:

```sh
elan toolchain install leanprover/lean4:v4.30.0
cd formal
lake exe cache get
cd ..
```

The setup downloads dependencies and compiled Mathlib objects. They are not
bundled in this source release. Keep the committed dependency pins when
reproducing the recorded results; do not use `lake update` to upgrade them.

## Replay

First check the inventory and its hashes without running Lean:

```sh
python bugbank/lean/replay.py --check-inventory
```

Compile all 312 files and inspect the selected declarations:

```sh
python bugbank/lean/replay.py
```

The command writes per-file compiler output and `summary.json` in `.replay/`.
Each source receives a separate Lean process. A pass requires successful
compilation, an axiom print for every selected declaration, and axiom sets
contained in `propext`, `Classical.choice`, and `Quot.sound`. This rejects
`sorryAx`, native-reduction axioms, and other additional axioms for the selected
declarations. The recorded audits in `selected_declarations.json` provide the
earlier declaration types and axiom lists for comparison.

Useful smaller selections:

```sh
python bugbank/lean/replay.py --group certificates --select SE_cs_97637
python bugbank/lean/replay.py --group mathematics --select SqrtFailureBoundary
python bugbank/lean/replay.py --group mathematics --exclude Cube8Mod36 --jobs 4
python bugbank/lean/replay.py --list
```

`--select` and `--exclude` match path substrings and can be repeated. The default
timeout is 600 seconds per file and 7200 seconds for `Cube8Mod36`; `--timeout`
overrides it. `--output` selects a different log
directory. `--mathlib-project PATH` can reuse an existing installation after
checking that its toolchain and full dependency manifest match this release.

The default runs one compiler at a time. `--jobs` permits parallel compilation
when memory allows. The largest file, `Cube8Mod36.lean`, took about 30–37 minutes
in the recorded successful builds; the original job reserved 160 GB of memory
(an allocation, not a measured minimum requirement). It can be replayed
separately on a suitable machine:

```sh
python bugbank/lean/replay.py --exclude Cube8Mod36 --jobs 4
python bugbank/lean/replay.py --select Cube8Mod36 --jobs 1 --timeout 7200 --output .replay-cube8
```

## Core-only follow-ups under Lean 4.34.0

Fifteen mathematical files use only Lean's bundled libraries and have recorded
builds under both 4.30.0 and 4.34.0. Their replay needs no Mathlib download:

```sh
elan toolchain install leanprover/lean4:v4.34.0
python bugbank/lean/replay.py --group mathematics --core-only --core-version 4.34.0 --output .replay-core-434
```

Mathlib-dependent files retain their recorded 4.30.0 environment.

## Evidence and interpretation

`replay_manifest.json` binds every source and its selected-declaration evidence
by SHA-256. Original indices, receipts, statements and proof bytes are retained.
The original receipts describe the inspection archive at the time it was made;
these replay instructions are an addition to that archive. New replay summaries
are separate from the saved build receipts.

The packaging check in `replay_validation.json` records fresh successful replay
of all 284 corpus certificates and 27 of the 28 mathematical files. Two
certificate processes interrupted during parallel execution passed on sequential
retry. The local `Cube8Mod36` process was terminated by signal 9; its earlier
successful builds under both toolchains remain in the supplied receipts. The
dependency setup check reused installed packages at the committed pins.

The kernel checks the selected formal statements. Source passages, assumptions,
and the review of their connection to those statements are in the corpus
records. The mathematical indices retain the precise scope and attribution of
each follow-up. Recompilation preserves those distinctions.
