r"""Inside the AimForCont argument the proof asserts the inclusion step \bigcup_{j = 1, j \ne i}^{m - 1} \paren{D_j \cup D_m} \subseteq \bigcup_{j = 1, j \ne i}^{m - 1} D_j, i.e. that the copy of D_m may simply be dropped from the union. This inclusion is false in general (the correct direction is the reverse), so the derivation of d_i \in E_i \subseteq \bigcup_{j \ne i}^{m-1} D_j is not justified by the stated steps."""

import itertools
import json

RECORD_ID = "proofwiki_133598"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "m = 3, i = 1, D_1 = empty, D_2 = empty, and D_3 = {0}."
)
REFUTATION_EXPLANATION = (
    "For m = 3 and i = 1, the only included index is j = 2. "
    "The left union is D_2 union D_3 = {0}, while the right union is "
    "D_2 = empty. Thus 0 belongs to the left side but not the right side, "
    "so the asserted inclusion fails."
)
SEARCH_SPACE = (
    "Exhaustively swept all 16 cases with m = 3, i in {1, 2}, universe "
    "{0}, and each of D_1, D_2, D_3 independently equal to either the "
    "empty set or {0}."
)


def compute_unions(sets_by_index, m, i):
    left = set()
    right = set()
    for j in range(1, m):
        if j != i:
            left.update(sets_by_index[j] | sets_by_index[m])
            right.update(sets_by_index[j])
    return frozenset(left), frozenset(right)


def main():
    universe = (0,)
    subsets = (frozenset(), frozenset({0}))
    witnesses = []
    cases_checked = 0

    for i in (1, 2):
        for choices in itertools.product(subsets, repeat=3):
            sets_by_index = {
                1: choices[0],
                2: choices[1],
                3: choices[2],
            }
            left, right = compute_unions(sets_by_index, 3, i)
            cases_checked += 1
            for element in universe:
                if element in left and element not in right:
                    witnesses.append((i, choices, element, left, right))

    assert cases_checked == 16
    assert witnesses
    first = witnesses[0]
    assert first == (
        1,
        (frozenset(), frozenset(), frozenset({0})),
        0,
        frozenset({0}),
        frozenset(),
    )

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
