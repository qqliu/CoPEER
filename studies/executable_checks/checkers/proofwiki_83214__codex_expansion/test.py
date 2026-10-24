r"""Equation (8): for 1 ≤ k ≤ n, ∑_{j=1}^n x_j e_k(X \ {x_j}) = k e_k(X)."""

import json

RECORD_ID = "proofwiki_83214__codex_expansion"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness can be stated from the permitted data, because no "
    "interpretation of e_k, X, or set subtraction is supplied."
)
REFUTATION_EXPLANATION = (
    "The displayed equation is not evaluable as a mathematical predicate from "
    "the quote alone: e_k is undefined, X is undefined, and the behavior of "
    "X \\ {x_j} is unspecified. Assigning standard elementary-symmetric-polynomial "
    "semantics would add definitions absent from the quote."
)
SEARCH_SPACE = (
    "The exact bounded sweep is the empty tuple of fully specified evaluations "
    "(0 cases), iterated in tuple order; no evaluation is admissible from the "
    "supplied data without inventing missing definitions."
)


def search():
    fully_specified_evaluations = ()
    for evaluation in fully_specified_evaluations:
        raise AssertionError("The permitted data unexpectedly supplied an evaluation")
    return {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }


if __name__ == "__main__":
    print(json.dumps(search(), sort_keys=True, separators=(",", ":"), ensure_ascii=False))
