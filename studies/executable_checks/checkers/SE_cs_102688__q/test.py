"""If Path P: s->...->u->v is a shortest path from s to v, then by the property of optimal substructure, the subpath s->...->u of P must also be a shortest path from s to u. Therefore, d(u) must equal to δ(s,u)."""

import itertools
import json

RECORD_ID = "SE_cs_102688__q"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No concrete witness can be evaluated because the quote does not define "
    "d(u) or relate it to the length of the displayed subpath."
)
REFUTATION_EXPLANATION = (
    "The quote states that the prefix is shortest, but that fact alone does not "
    "determine the separately written quantity d(u). All 8 propositional truth "
    "assignments to the three quoted assertions were checked; the assignment "
    "(whole path shortest, prefix shortest, d(u) != delta(s,u)) shows the missing "
    "logical relation, but it is not a concrete graph counterexample without "
    "definitions for d and delta."
)
SEARCH_SPACE = (
    "Exactly the 8 assignments in {False, True}^3, in itertools.product order, "
    "for: (P is shortest from s to v, its prefix is shortest from s to u, d(u) "
    "equals delta(s,u)). This is an exhaustive propositional diagnostic, not an "
    "exhaustive space of graphs."
)


def main():
    unresolved = []
    examined = 0
    for whole_is_shortest, prefix_is_shortest, distances_equal in itertools.product(
        (False, True), repeat=3
    ):
        examined += 1
        if whole_is_shortest and prefix_is_shortest and not distances_equal:
            unresolved.append(
                (whole_is_shortest, prefix_is_shortest, distances_equal)
            )

    assert examined == 8
    assert unresolved == [(True, True, False)]

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
