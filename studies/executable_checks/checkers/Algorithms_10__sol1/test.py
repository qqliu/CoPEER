"""Lemma 1. The minimum degree satisfies delta(G) > alphan."""

import json

SUPPLIED_CONCRETE_GRAPHS = ()
SUPPLIED_EXACT_ALPHAN_VALUES = ()

REPORT = {
    "record_id": "Algorithms_10__sol1",
    "outcome": "NO_WITNESS_INCONCLUSIVE",
    "witness_description": "No witness is claimed; the quote supplies no concrete graph G and no exact value or definition of alphan.",
    "refutation_explanation": "The inequality cannot be evaluated from the supplied quote alone. Searching invented graphs or invented meanings of alphan would not constitute a counterexample to the stated claim.",
    "search_space": "The exact finite space swept is the Cartesian product of supplied concrete graphs () and supplied exact alphan values (); it contains 0 candidate instances.",
}

checked_instances = 0
first_witness = None
for graph in SUPPLIED_CONCRETE_GRAPHS:
    for alphan in SUPPLIED_EXACT_ALPHAN_VALUES:
        checked_instances += 1
        raise AssertionError(
            "A candidate unexpectedly exists without supplied evaluation semantics"
        )

computed_outcome = (
    "NO_WITNESS_INCONCLUSIVE"
    if first_witness is None and checked_instances == 0
    else "WITNESS_FOUND"
)
assert computed_outcome == REPORT["outcome"]
assert first_witness is None
assert checked_instances == len(SUPPLIED_CONCRETE_GRAPHS) * len(
    SUPPLIED_EXACT_ALPHAN_VALUES
)
assert set(REPORT) == {
    "record_id",
    "outcome",
    "witness_description",
    "refutation_explanation",
    "search_space",
}

print(json.dumps(REPORT, separators=(",", ":")))
