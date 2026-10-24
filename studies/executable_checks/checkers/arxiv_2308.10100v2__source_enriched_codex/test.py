"""The bijection between the FC monomial basis indexed by $A_n^c$ and the non-crossing diagrams on $n+1$ strings that respects products is unique."""

import itertools
import json

RECORD_ID = "arxiv_2308.10100v2__source_enriched_codex"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete pair of distinct product-respecting bijections can be formed "
    "from the supplied data."
)
REFUTATION_EXPLANATION = (
    "The quote asserts uniqueness but supplies neither a fixed value of n nor "
    "explicit elements, products, diagrams, or candidate maps. Consequently, "
    "the claim cannot be tested for a counterexample without inventing absent "
    "definitions or data."
)
SEARCH_SPACE = (
    "The complete bounded set of concretely specified candidate bijections in "
    "the permitted quote: the empty set; itertools.combinations((), 2) "
    "therefore contains exactly 0 pairs."
)


def main():
    candidate_bijections = ()
    distinct_pairs = tuple(itertools.combinations(candidate_bijections, 2))
    assert len(distinct_pairs) == 0

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
