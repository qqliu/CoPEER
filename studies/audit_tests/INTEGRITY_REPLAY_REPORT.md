# Six-fixture integrity replay: public scientific projection

Source: the recorded 25 September 2026 integrity-replay report (v2), with the final result from 19:02:26–19:02:30 UTC. The report was prepared with Claude Opus 5; the replay itself made no model calls, ran no Lean, and used no network. This is a bounded application of production functions to specified fixtures, not independent unseen attack validation.

| Fixture | Mutation | Saved outcome | Meaning |
|---|---|---|---|
| V1 | Build receipt bound to different Lean source bytes | Refused | Source-byte identity; not a test of whether a different theorem name in unchanged bytes has adequate semantics. |
| V2 | Card changed without updating its review receipt | Refused | The source-authority check refused it earlier than the predicted publisher stage. The predicted later stage remains untested by this fixture. |
| V3 | Source-line texts swapped and all dependent hashes rebound | Accepted | Gold remained line2 while its text became line7. Mechanical consistency does not establish source correspondence. |
| V4 | Recorded selected declaration audit lists unauthorized axioms | Refused | The publisher checks producer-supplied audit flags; it does not itself extract Lean dependencies. |
| V5 | Duplicate record identity, preserving total row count | Refused | Duplicate identity check. |
| V6 | Historical charged-token aggregate increased by one | Refused | Cost-accounting sum check, not a general accuracy-aggregate check. |

Five fixtures were refused and one accepted. All detection predictions matched; V2's reason/stage prediction did not. The saved JSON preserves every outcome and the deviation.

Original recorded controls: 43 scorer tests, 25 dispatch tests, 47 extension-builder tests and 54 bank tests (169 total), plus 22 development tests. Eight saved Lean-mutant rows were inspected without rerunning Lean. Their logs and receipts are historical evidence. This package includes the code closure for the six fixtures and 21 synthetic development tests, including three named clean positive controls. One development test needs protected historical release inputs and is excluded from the public convenience command, as documented in README.md. Full legacy suite closure is not claimed.

No package reproduction was executed during assembly. Source-byte validation, source interpretation, Lean theorem validity and full pipeline behavior remain distinct. The source report's earlier run timestamp and original v1 intermediate-result hash were superseded by the final result binding in v2; scientific outcomes did not change.
