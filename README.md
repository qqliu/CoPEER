# Co-PEER: Auditing Mathematics with Proofs of Error

Co-PEER (Collaborative Proof Expert Evaluation Review) is a workflow for constructing and checking *proofs of error*: objections to mathematical arguments that come with their own evidence. Each *objection dossier* records the challenged source passage and its assumptions, a concrete counterexample, a Lean-checked certificate, a review of whether the formal statement corresponds to the source claim, and the revision history. **BugBank** is the collection that stores the dossiers.

This repository holds the paper, the project website, and the released evidence behind every result in the paper.

Anna Gilbert¹, Stephen Xia¹, Kirill Acharya², Shayan Hundrieser¹, Benjamin Li³, Jan Ondras⁴, Vaishali Surianarayanan¹, Jason Wang⁵, Joon-Hyeok Yim¹, Arman Cohan¹, Quanquan C. Liu¹
¹ Yale University · ² Stanford University · ³ University of Oxford · ⁴ Massachusetts Institute of Technology · ⁵ The Innovation Fellowship

**Paper:** [`paper/co-peer.pdf`](paper/co-peer.pdf) (preprint; arXiv identifier pending). **Website:** https://qqliu.github.io/CoPEER/ (the `docs/` folder). **Terms of use:** [`NOTICE.md`](NOTICE.md).

## What is where

| Folder | Contents |
| --- | --- |
| [`paper/`](paper/) | The paper (PDF and arXiv source) and its figure files. |
| [`docs/`](docs/) | The project website: an interactive example, the BugBank explorer, the benchmark results, the studies and the mathematics. |
| [`bugbank/`](bugbank/) | The released dossiers: for each record a dossier, its numbered source text and its Lean certificate; the human-approved core; the human-review records; the source annotations. |
| [`benchmark/`](benchmark/) | The certified-claim localization benchmark: inputs, saved model answers, parsed selections, scores, scoring code and the replay. |
| [`studies/`](studies/) | The instruction study, the repair tasks, the proof-development study, the open-problem retrieval study, the review of saved responses, the executable checks and the audit tests. |
| [`mathematics/`](mathematics/) | Lean sources and records for the mathematical follow-ups: `theorems/` (the family theorems), `extensions/` (the further certified families), `explanations/` (the thirteen packages), `discoveries/`. |
| [`tools/`](tools/) | The file verifier and the scripts that build the website's data. |

Every folder has a README that says what its files are, how to read them, and how to check them. `MANIFEST.json` lists every file with its SHA-256 hash; `ARTIFACTS.md` connects each result in the paper to its files and replay command; `THIRD_PARTY_NOTICES.md` covers the source passages and dependencies; `requirements.txt` lists the two optional Python packages.

## Quick start

The commands below need only Python 3 and its standard library; none of them makes model calls. Two replays need more: the instruction study's interval analysis needs NumPy (`tools/requirements-analysis.txt`) and the audit tests need PyYAML (`studies/audit_tests/requirements.txt`; both are listed in `requirements.txt`).

```sh
python3 -B tools/verify.py --strict                                   # every file matches MANIFEST.json
python3 -B bugbank/core/verify.py --release .                          # the 147-dossier human-approved core and its bindings
python3 -B benchmark/core/replay.py --release . --membership bugbank/core/membership.json --output /tmp/core_scores.json --with-intervals
python3 -B bugbank/reviews/reproduce.py --check                        # the human-review counts
python3 -B bugbank/lean/replay.py --check-inventory                    # the certificate inventory
```

Each study's README under `studies/` gives its reproduction command. Compiling the Lean certificates and the mathematical follow-ups additionally requires the pinned toolchain described in `bugbank/lean/README.md` and `mathematics/README.md`.

## The populations, kept apart

- The **BugBank collection**: every dossier the workflow produced; membership is not human approval. The release contains the 284 screened dossiers of the evaluated collection.
- The **human-approved core**: 147 dossiers from 137 distinct sources with all-YES human judgments on the three review questions and recorded version continuity (`bugbank/core/membership.json`).
- The **benchmark inputs**: 100 primary texts from 92 problem clusters (at least ten nonblank lines), plus 31 shorter supplementary texts, 131 scorable inputs in all.

## Citation

```bibtex
@article{copeer2026,
  title   = {Co-PEER: Auditing Mathematics with Proofs of Error},
  author  = {Gilbert, Anna and Xia, Stephen and Acharya, Kirill and Hundrieser, Shayan and Li, Benjamin and Ondras, Jan and Surianarayanan, Vaishali and Wang, Jason and Yim, Joon-Hyeok and Cohan, Arman and Liu, Quanquan C.},
  year    = {2026},
  note    = {Preprint; identifier pending}
}
```

## Terms of use

See [`NOTICE.md`](NOTICE.md). In short: the authors' text, data and code are for reading, checking and citing; the contents may not be used to train or fine-tune machine-learning models or be scraped for that purpose; third-party source passages keep their own authorship and terms.
