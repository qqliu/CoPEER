# Corpus audit guidance derived from human responses

This checklist is an automated audit plan derived from the comments, not a new human verdict. Apply it to every record, including previously all-YES records. Preserve each human response unchanged.

1. **Recover the complete challenged assertion and its hypotheses.** Check previous sentences, definitions, case restrictions, and the actual scope of quantifiers. A quote alone can be verbatim while losing its hypothesis. Examples: prior graph isomorphism (`reddit_learnmath_o65dcu`), no universal vertex (`mse_3369465__ans3369504`), minimal face (`Algorithms_47__sol4`), disconnected colored components (`Graph_Theory_20__sol4`), angle range (`mse_4217205__ans4217514`), and restricted integer range (`proofwiki_56736`).
2. **Establish that the challenged passage asserts a proposition.** A conditional branch or intermediate algorithmic test need not be true on all inputs (`arxiv_2505.21645v2__source_enriched_codex`). Keep literal source text distinct from an interpretation of its meaning. Do not treat asymptotic equality as literal equality (`SE_math_4219732__q`). Label typographical slips separately from substantive proof errors.
3. **Check every witness assumption.** Recalculate domain membership, lower bounds, cardinalities, distinctness modulo symmetry, graph conditions, probability normalization, and conventions such as zero in the naturals or gcd(0,0). Do not use a finite boundary case to refute an eventual or asymptotic assertion (`mse_4580215__ans4585306`). The bipartition with swapped sides may be the same partition (`Algorithms_35__sol5`).
4. **Check dependencies among parameters.** A constant chosen as a function of a radius cannot then be held independent of that radius (`reddit_learnmath_1h7q3ju`). Match the order of existential and universal quantifiers and all side conditions.
5. **Match the mathematical objects in Lean.** Prefer established Mathlib definitions and theorems. Arithmetic encodings, rational surrogates, opaque definitions, user axioms, and abstract propositions require explicit proved connections to the intended real, analytic, probabilistic, or graph objects. A number called an integral is not an integral theorem (`arxiv_1510.03522v1__source_enriched_codex`, `proofwiki_116604__codex_expansion`); a defined Wick trace expression is not itself the Gaussian trace moment (`mse_811862__ans811879`).
6. **Match the exact logical statement and selected theorem.** To refute P implies Q prove P and not Q, not merely not(P and Q). Inspect the theorem actually selected in the certificate and packet, not just whether some correct theorem exists elsewhere (`Graph_Theory_12__sol5`, `reddit_compsci_2p76am`). A finite numerical range does not establish the proposed universal counterexample (`SE_cs_142560__q`).
7. **Check complete reductions and interpretation bridges.** When a finite certificate stands for planarity, a ceiling/logarithm identity, or another mathematical property, identify and prove the bridge or state the certification limit honestly (`mse_4554797__ans4598075`, `arxiv_2508.14831v4__source_enriched_codex`).
8. **Keep narrative, source quotation, and theorem scope synchronized.** Enumerate all cases that the Lean theorem excludes (`mse_3739826__ans3740014`); provide the definition of the function used by the counterexample (`SE_cs_1957__a2388`); align initial values (`reddit_askmath_1kp2tga`); show the relevant source context rather than unrelated introductory paragraphs.
9. **Record missing provenance and uncertainty.** A deleted source with a local transcription can still be studied, but a reviewer who could not establish fidelity remains inconclusive. Do not silently turn CANNOT DETERMINE into YES. Restore readable mathematical notation and label transcriptions.
10. **Track dispositions explicitly.** Repair a defensible record with an exact explanation and fresh compile evidence; otherwise quarantine it pending source/formalization work. A successful compile does not settle source fidelity. Human acceptance applies to the reviewed artifact and is not transferred automatically to edited artifacts.

## All-YES reviews with additional reservations

These records still count among the 61 original all-YES responses. Their comments should inform the broader audit:

- `proofwiki_39530__codex_expansion`: reviewer notes the proof appears to use metric neighborhoods within a generic topological claim.
- `reddit_askmath_1qurv0t`: reviewer says the source proof image was inaccessible and the detected issue is an auxiliary prime exception rather than the main proof flaw.
- `reddit_learnmath_3q7al0`: reviewer calls the equation a likely typo and expresses uncertainty about answering YES to source fidelity.
- `reddit_learnmath_bwiq68`: reviewer recommends another reviewer because of uncertainty about abstract algebra.
- `reddit_learnmath_18emvdx`: reviewer identifies a typo that does not affect later computations.
- `reddit_askmath_ls1zn5`: reviewer describes the asserted passage as a possible author typo.

No count in this directory treats these reservations as a replacement answer; the original YES/NO/CANNOT DETERMINE cells determine the reported historical count.
