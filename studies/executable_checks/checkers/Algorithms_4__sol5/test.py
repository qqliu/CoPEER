"""Every vertex in L has degree exactly n3/4 (by construction)."""

import json

TARGET_CLAIM = "Every vertex in L has degree exactly n3/4 (by construction)."
SOURCE_QUOTE = "Every vertex in L has degree exactly n3/4 (by construction)."

# Each entry would be a pair (description, violates_claim) obtained from an
# explicitly specified graph/construction instance. The supplied sentence
# specifies no such instance, so this exact bounded candidate space is empty.
EXPLICIT_CANDIDATE_INSTANCES = ()

first_witness = None
checked = 0
for description, violates_claim in EXPLICIT_CANDIDATE_INSTANCES:
    checked += 1
    if violates_claim:
        first_witness = description
        break

if first_witness is not None:
    computed_outcome = "WITNESS_FOUND"
elif checked == 0:
    computed_outcome = "NO_WITNESS_INCONCLUSIVE"
elif checked == len(EXPLICIT_CANDIDATE_INSTANCES):
    computed_outcome = "NO_WITNESS_EXHAUSTIVE"
else:
    raise AssertionError("candidate sweep ended inconsistently")

computed_search_space = (
    "The exact finite space swept is the empty tuple of graph/construction "
    "instances explicitly specified by the sole supplied sentence ("
    + str(len(EXPLICIT_CANDIDATE_INSTANCES))
    + " instances)."
)

REPORT = {
    "record_id": "Algorithms_4__sol5",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No concrete witness is available because the supplied sentence specifies no candidate graph or construction to test.",
    "refutation_explanation": "The source quote is identical to the claim and supplies no definition of L, n3, an ambient graph or edge set, or the referenced construction. Therefore the degree equality cannot be evaluated, and neither a counterexample nor exhaustive support over the intended instances follows.",
    "search_space": "The exact finite space swept is the empty tuple of graph/construction instances explicitly specified by the sole supplied sentence (0 instances).",
}

assert SOURCE_QUOTE == TARGET_CLAIM
assert first_witness is None or computed_outcome == "WITNESS_FOUND"
assert computed_outcome == REPORT["outcome"]
assert computed_search_space == REPORT["search_space"]

print(json.dumps(REPORT, separators=(",", ":")))
