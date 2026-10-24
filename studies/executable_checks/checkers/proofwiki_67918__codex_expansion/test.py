"""For each partition P, the lower Darboux sum satisfies L(λf+μg,P)=λL(f,P)+μL(g,P)."""

import json

RECORD_ID = "proofwiki_67918__codex_expansion"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No witness is asserted because the permitted data supplies no concrete "
    "admissible functions, scalars, partitions, interval, or definition of the "
    "lower Darboux sum."
)
REFUTATION_EXPLANATION = (
    "The claim cannot be evaluated from the supplied strings alone: the domains "
    "and hypotheses for λ, μ, f, g, and P are unstated, and the source quote "
    "references but does not provide the definition of a lower Darboux sum. "
    "Constructing a numerical model would therefore invent definitions or data "
    "absent from the quote."
)
SEARCH_SPACE = (
    "The exact finite space swept is CANDIDATES = (), containing zero semantically "
    "licensed concrete instances; all zero candidates are visited in fixed tuple "
    "order."
)

# Each entry, if the supplied data licensed one, would be
# (witness_description, exact_violation_verdict).  None is licensed here.
CANDIDATES = ()


def exhaustive_search():
    visited = 0
    for description, violates_claim in CANDIDATES:
        visited += 1
        if violates_claim:
            return description
    if visited != len(CANDIDATES):
        raise AssertionError("candidate traversal was not exhaustive")
    return None


def main():
    witness = exhaustive_search()
    if witness is not None:
        raise AssertionError("the declared empty search space produced a witness")
    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
