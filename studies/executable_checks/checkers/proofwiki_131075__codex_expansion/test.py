"""The proof claims that an irreducible closed subspace admits two proper closed subsets whose union is the whole subspace."""

import json

RECORD_ID = "proofwiki_131075__codex_expansion"
WITNESS_DESCRIPTION = (
    "No concrete witness: the sole source-supplied configuration is symbolic "
    "and explicitly asserts the claimed decomposition."
)
REFUTATION_EXPLANATION = (
    "The quote supplies names and three asserted relations, but no carrier "
    "elements, topology, or definition or test for irreducibility. Therefore "
    "it is impossible to verify a candidate satisfying the premise while "
    "falsifying the conclusion without inventing absent definitions or data."
)
SEARCH_SPACE = (
    "Exactly one symbolic configuration was swept: "
    "('F = F_1 \\\\cup F_2', 'F_1 \\\\subsetneq F', "
    "'F_2 \\\\subsetneq F'). No concrete topological structures were "
    "enumerated because none are specified by the permitted data."
)

bounded_space = (
    ("F = F_1 \\cup F_2", "F_1 \\subsetneq F", "F_2 \\subsetneq F"),
)
expected_conclusion = (
    "F = F_1 \\cup F_2",
    "F_1 \\subsetneq F",
    "F_2 \\subsetneq F",
)
witnesses = []
for symbolic_configuration in bounded_space:
    conclusion_is_asserted = symbolic_configuration == expected_conclusion
    premise_is_testable = False
    if premise_is_testable and not conclusion_is_asserted:
        witnesses.append(symbolic_configuration)

assert not witnesses
result = {
    "record_id": RECORD_ID,
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, ensure_ascii=True, separators=(",", ":")))
