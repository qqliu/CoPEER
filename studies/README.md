# The studies

Each study has its own inputs, protocol and saved results, and its README gives the command that recomputes the reported numbers from the saved records without making model calls (Python 3; the instruction study's interval analysis needs NumPy and the audit tests need PyYAML).

| Folder | Study | Where the paper reports it |
| --- | --- | --- |
| `instructions/` | Four instruction arms on 100 proofs and on 60 statements: counterexample-first search, full verification or proof attempt, ordinary early stop, early stop with a counterexample required; confirmed objections and token accounting. | the instruction-study results and their token accounting, and the instruction-study appendix |
| `repairs/` | Sixteen Lean repair tasks in which the identified defect and the correction to prove are given, with and without the checked counterexample. | the repair-task results |
| `proof_development/` | Fifty paired proof-revision tasks per model with and without retrieval of earlier objections. | the proof-development results |
| `open_problem_retrieval/` | Retrieval during open-problem search: the five cohorts of paired targets. | the open-problem retrieval results |
| `response_review/` | The LLM review of saved critic responses on 24 paired texts (Experiment B). | the saved-evidence review (Experiment B) |
| `executable_checks/` | The 604 executable search tasks and the separately written checkers; `bindings/` holds the program bindings and the sixteen selected algorithmic failures. | the construction workflow and the executable-checks appendix |
| `criticism_endpoints/` | The joint criticism-and-paired-comparison bounds computed from the saved Experiment B panel (24 inputs, 48 attempts); `analyze_existing_evidence.py` recomputes them. | the conditional-interval remark in the score-theory appendix |
| `audit_tests/` | Six publication/scoring fixtures: a wrong declaration, a stale receipt, rebound source text, an unauthorized axiom, a duplicate record and a corrupted aggregate. `attack_set/run_attack_set.py` reproduces the six-fixture result; `run_selected_tests.py` runs three clean controls, and `--synthetic-tests` runs 21 selected tests (PyYAML). | the procedures appendix |

`replay_reviewed_projections.py` with `reviewed_projection_bindings.json` replays the projections of the instruction-study records that were reviewed.
