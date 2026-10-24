r"""For each $p=\langle x,y\rangle\in P$ let $\succeq_p$ be a linear order on $X$ extending $\succeq$ and such that $x\succeq_p y$."""

import json


RECORD_ID = "mse_424518__ans424960"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness is asserted because the supplied quote specifies no concrete "
    "candidate structure."
)
REFUTATION_EXPLANATION = (
    "The claim does not define X, P, or the relation \\succeq, and states no "
    "hypotheses that would determine whether the required linear orders exist. "
    "Under the blind-data restriction, constructing an interpretation would "
    "invent absent data, so the empty candidate sweep is inconclusive."
)
SEARCH_SPACE = (
    "All fully specified finite candidate structures explicitly supplied by "
    "target_claim and source_quote: the empty set (0 candidates)."
)


def main():
    candidate_structures = ()
    witness = None
    for candidate in candidate_structures:
        witness = candidate
        break
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
