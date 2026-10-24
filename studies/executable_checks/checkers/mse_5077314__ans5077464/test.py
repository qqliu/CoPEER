r'''Therefore every $r$-element set containing $a_r$ but not $a_0$ is in $\mathcal A$, because any such set can be $\{a_r, a_{r+1}, \dots, a_{2r-1}\}$ for some cyclic order.'''

import itertools
import json

RECORD_ID = "mse_5077314__ans5077464"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No counterexample is certified. The bounded indexing audit found no "
    "representation failure, but membership in the undefined family \\mathcal A "
    "cannot be tested."
)
REFUTATION_EXPLANATION = (
    "The quote does not define \\mathcal A, the ambient ground set, the "
    "admissible cyclic orders, or the quantified range of r. Consequently, a "
    "finite search cannot decide the asserted membership conclusion. The "
    "program only verifies the representation statement under its explicitly "
    "declared finite indexing convention."
)
SEARCH_SPACE = (
    "Illustrative audit only: for each integer r from 1 through 4, all 29 "
    "r-subsets of {a_0,...,a_{2r-1}} containing a_r and excluding a_0 were "
    "checked against every order representative fixing a_0 at position 0 and "
    "a_r at position r. This sweeps 14,549 exact (set, order) pairs; it is not "
    "an exhaustive search of the source claim."
)


def run_audit():
    candidate_count = 0
    pair_count = 0
    failures = []

    for r in range(1, 5):
        movable = tuple(i for i in range(1, 2 * r) if i != r)
        orders = []
        for permutation in itertools.permutations(movable):
            order = (
                (0,)
                + permutation[:r - 1]
                + (r,)
                + permutation[r - 1:]
            )
            orders.append(order)

        for chosen in itertools.combinations(movable, r - 1):
            candidate = frozenset((r,) + chosen)
            candidate_count += 1
            represented = False
            for order in orders:
                pair_count += 1
                block = frozenset(order[r:2 * r])
                if block == candidate:
                    represented = True
            if not represented:
                failures.append((r, tuple(sorted(candidate))))

    assert candidate_count == 29
    assert pair_count == 14549
    assert failures == []


run_audit()
print(json.dumps({
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}, separators=(",", ":")))
