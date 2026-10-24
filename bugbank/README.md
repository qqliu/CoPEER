# BugBank: the released objection dossiers

A dossier is one objection to one assertion in a mathematical source. For every released record `<record-id>` there are three files:

| File | What it is |
| --- | --- |
| `dossiers/<record-id>.json` | The dossier: the quoted challenged claim and its assumptions, the counterexample (witness) and its explanation, the selected Lean declaration with the axioms it uses, and the record's benchmark roles. |
| `sources/<record-id>.json` | The numbered source text the critics saw, with the reference-line labels and the problem cluster. |
| `certificates/<record-id>.lean` | The Lean certificate: a proof that the encoded assumptions hold and the encoded conclusion fails for the witness. |

`index.json` lists the 284 released records with their source collection, benchmark roles and file paths. Membership in the collection is not human approval; the human-review layer is separate:

| Folder | What it is |
| --- | --- |
| `core/` | The **human-approved core**: `membership.json` names the 147 dossiers (from 137 distinct sources) with all-YES human judgments on the three review questions and recorded version continuity, with each record's review evidence, current reference lines and the hashes that bind it to its files; `verify.py` checks all of it. |
| `reviews/` | The human-review rounds, deidentified: answers to the three questions for each reviewed record, the review packets, the reference-line checks, the version resolutions and the matched replacement witnesses. Its README maps each folder to the round reported in the paper. |
| `annotations/` | The saved annotations of the records (error mechanism, object kind, refutation role) and the census tables the paper's composition counts come from. |
| `review-continuity/` | The records that link reviewed versions of a dossier to the current files. |
| `support/` | Recovered primary-source documents, with their original authorship. |
| `lean/` | The pinned Lean environment, the certificate inventory with hashes and axiom audits, and the replay script for the certificates. |

The three review questions are: Q1, does the dossier read the source claim correctly; Q2, is the counterexample valid under the source's assumptions; Q3, does the Lean statement correspond to the claim and the witness.

Check it:

```sh
python3 -B bugbank/core/verify.py --release .          # core membership, bindings and review tables
python3 -B bugbank/reviews/reproduce.py --check        # review counts
python3 -B bugbank/lean/replay.py --check-inventory
```

Two things to know when reading a dossier file: the fields `evidence_tier` and `human_approval_of_current_artifact` are the values recorded when the dossier was exported automatically, before the human reviews; the current human-review verdict for a record is the entry in `core/membership.json`, joined by record id. Path strings inside the dossier files use the layout of this repository (`bugbank/sources/…`, `bugbank/certificates/…`).
