r"""We know that $S - e^\prime + e$ is a Spanning Tree. Therefore $e$ must be a bridge between $S_1$ and $S_2$."""

import json

RECORD_ID = "SE_math_4220496__q"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No witness is reported because the quote does not define the objects needed to evaluate one."
REFUTATION_EXPLANATION = "The premise only says that S - e' + e is a spanning tree. The quote does not define S1 and S2, say how they are obtained, specify the ambient graph, or define 'bridge between'. Thus no well-defined counterexample predicate is available without adding assumptions."
SEARCH_SPACE = "Exactly the empty candidate set (0 candidates): no graph instances can be constructed from the supplied quote without inventing the missing definitions and data."


def main():
    candidates = ()
    witness = None
    for candidate in candidates:
        witness = candidate
    assert witness is None
    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
