r"""We shall prove that, for any fixed $k,n$ with $n$ having the prime decomposition above, there is a prime $p$, and integer $q$, and a positive integer $m$, such that $pq^m \equiv k\pmod{p_j^{a_j}}$, for every $1\leq j\leq K$."""

import json

RECORD_ID = "mse_3160594__ans3160616"
FULLY_SPECIFIED_CONGRUENCE_SYSTEMS = ()
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No concrete witness is claimed."
REFUTATION_EXPLANATION = (
    "The supplied quote refers to a prime decomposition \"above\" but does not "
    "supply K or the pairs (p_j, a_j), so no concrete congruence system can be "
    "formed. It also gives no finite bounds for the existential variables p, q, "
    "and m. Consequently, failure within an invented bounded range would not "
    "refute the claim."
)
SEARCH_SPACE = (
    "The exact finite space swept is the empty set of fully specified congruence "
    "systems present in the supplied quote; its cardinality is 0."
)


def search():
    for system in FULLY_SPECIFIED_CONGRUENCE_SYSTEMS:
        raise AssertionError(system)
    return {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }


print(json.dumps(search(), separators=(",", ":")))
