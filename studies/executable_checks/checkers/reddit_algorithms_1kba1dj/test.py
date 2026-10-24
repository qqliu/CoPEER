"""The stated recurrence correctly computes F(t,i), the minimum cost for each feasible end-of-period inventory state i."""

import json
from itertools import product


def assess_assignment(i, x_t, d_t):
    """Evaluate all mechanically specified arithmetic for one bounded assignment."""
    predecessor = i + x_t - d_t
    # The source supplies no independent specification of the correct value of F,
    # so this exact computation alone cannot certify a counterexample.
    return predecessor, None


def main():
    examined = 0
    witness = None

    for i, x_t, d_t in product(range(5), repeat=3):
        predecessor, verdict = assess_assignment(i, x_t, d_t)
        assert predecessor == i + x_t - d_t
        examined += 1
        if verdict is not None and witness is None:
            witness = (i, x_t, d_t, predecessor, verdict)

    assert examined == 125
    assert witness is None

    result = {
        "record_id": "reddit_algorithms_1kba1dj",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness can be certified from the supplied quote.",
        "refutation_explanation": "The quote gives a recurrence and base values but does not specify the demands d_t, the cost functions p_c{t}, the feasible inventory domain, or an independent definition of F against which correctness can be checked. The bounded exact sweep can evaluate the displayed index constraint, but treating any assignment as a counterexample would require inventing missing semantics.",
        "search_space": "All 125 ordered triples (i, x_t, d_t) in {0,1,2,3,4}^3, in lexicographic product order; for each, the exact integer i'=i+x_t-d_t was computed. This is an illustrative diagnostic sweep, not an exhaustive space of problem instances."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
