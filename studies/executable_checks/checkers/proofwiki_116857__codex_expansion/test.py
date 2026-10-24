r"""There exists exactly one sequence of diagonal neighborhoods satisfying V_0 = V, symmetry of V_n for every n > 0, and V_n \circ V_n \subseteq V_{n-1} for every n > 0."""

import json
from itertools import product

RECORD_ID = "proofwiki_116857__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Let X = {0,1} have the discrete topology, let Delta = "
    "{(0,0),(1,1)}, and set V = X x X. One sequence has V_0 = V "
    "and V_n = Delta for every n > 0; another has V_n = V for every n >= 0."
)
REFUTATION_EXPLANATION = (
    "Both sequences consist of neighborhoods of Delta and are symmetric at every "
    "positive index. For the first, Delta composed with Delta is Delta, which is "
    "contained in V_0 and every later Delta. For the second, V composed with V is V. "
    "The sequences disagree at n = 1, so the asserted uniqueness fails."
)
SEARCH_SPACE = (
    "For X = {0,1} with the discrete topology and V = X x X, the program "
    "exhaustively checks all 16 binary relations R on X as the constant "
    "positive-index tail in templates V_0 = V and V_n = R for every n > 0."
)

X = (0, 1)
PAIRS = tuple(product(X, repeat=2))
DELTA = frozenset((x, x) for x in X)
UNIVERSAL = frozenset(PAIRS)

# Every subset is open in the discrete topology.
TOPOLOGY = tuple(
    frozenset(PAIRS[index] for index in range(len(PAIRS)) if mask & (1 << index))
    for mask in range(1 << len(PAIRS))
)


def is_neighborhood_of_diagonal(relation):
    return any(DELTA <= open_set <= relation for open_set in TOPOLOGY)


def is_symmetric(relation):
    return relation == frozenset((right, left) for left, right in relation)


def compose(relation):
    return frozenset(
        (left, right)
        for left in X
        for middle in X
        for right in X
        if (left, middle) in relation and (middle, right) in relation
    )


valid_tails = []
for mask in range(1 << len(PAIRS)):
    tail = frozenset(
        PAIRS[index] for index in range(len(PAIRS)) if mask & (1 << index)
    )
    if not is_neighborhood_of_diagonal(UNIVERSAL):
        continue
    if not is_neighborhood_of_diagonal(tail):
        continue
    if not is_symmetric(tail):
        continue
    tail_square = compose(tail)
    if not tail_square <= UNIVERSAL:
        continue
    if not tail_square <= tail:
        continue
    valid_tails.append(tail)

assert DELTA in valid_tails
assert UNIVERSAL in valid_tails
assert DELTA != UNIVERSAL

print(json.dumps({
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}))
