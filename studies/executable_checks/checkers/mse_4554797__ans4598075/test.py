"""Moreover, the $18$-edge example is unique, since the $12$-edge and $6$-edge pieces we joined along a cut vertex are unique: it must be three copies of $K_4$ joined at a cut vertex."""

import json
from itertools import combinations
from math import comb


RECORD_ID = "mse_4554797__ans4598075"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness is asserted. The quote does not define what qualifies as an “18-edge example” "
    "or what equivalence relation governs uniqueness."
)
REFUTATION_EXPLANATION = (
    "The supplied text states the uniqueness conclusion and its proposed decomposition, but "
    "gives no admissibility predicate for examples or pieces. Therefore, a nonisomorphic graph "
    "with 18 edges cannot be certified as a counterexample from the permitted data alone."
)
SEARCH_SPACE = (
    "Exhaustively enumerated all 1,330 simple labeled graphs on the fixed vertex set "
    "{0,1,2,3,4,5,6} having exactly 18 of the 21 possible edges, in lexicographic combination "
    "order. This illustrative bounded sweep cannot decide the claim because the quote supplies "
    "no predicate selecting the relevant examples."
)


def main():
    vertices = tuple(range(7))
    possible_edges = tuple(combinations(vertices, 2))
    searched = 0

    for encoded_graph in combinations(possible_edges, 18):
        assert len(encoded_graph) == 18
        searched += 1
        # No source-defined admissibility or uniqueness predicate exists, so none
        # of these exact encodings can honestly be classified as a counterexample.

    assert len(possible_edges) == 21
    assert searched == comb(21, 18) == 1330

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=False))


if __name__ == "__main__":
    main()
