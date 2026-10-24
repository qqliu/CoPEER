# Joint criticism and paired comparison bounds

This analysis uses the saved Experiment B panel: 24 inputs and 48 attempts, with one
Gemini and one Nemotron attempt per input. It combines the recorded LLM judgments
and adjudications to evaluate whether each attempt challenges the selected claim
with valid evidence. It also reproduces the finite-panel bounds from Appendix Q.3.

From the package root, using Python 3's standard library:

```sh
python -B studies/criticism_endpoints/analyze_existing_evidence.py --release . --output /tmp/copeer_joint_criticism.json
```

All seven required input files are included: the saved Experiment B review and
adjudication records, its protocol and source-scope review, and the original
benchmark inputs and selections. `EXISTING_EVIDENCE_RESULTS.json` is the saved
result. The replay uses existing judgments and makes no new model calls.

The joint endpoint requires a valid response, a challenge to the selected claim,
and valid supporting evidence. The 24-input panel is analyzed separately from
the retained-core benchmark. Bounds concern this finite panel under the named
judgments and assumptions; sampling confidence intervals are separate quantities.
