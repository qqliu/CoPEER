"""From each of $S_1,S_k$ we have to choose exactly $n/2$ elements, thus $n$ elements from both sets. By Pigeonhole principle there exists some $x_i$, such that it is chosen from both $S_1,S_k$ thus forming an edge with both $x_1$ and $x_k$."""

import json
from itertools import combinations

RECORD_ID = "SE_math_2803642__q"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Let n=4 and S_1=S_k={x_1,x_2,x_3,x_4}. Choose A={x_1,x_2} "
    "from S_1 and B={x_3,x_4} from S_k. Each choice has exactly n/2=2 "
    "elements, but A and B are disjoint."
)
REFUTATION_EXPLANATION = (
    "The stated premise is satisfied, yet no x_i is chosen from both sets. "
    "Choosing n elements in total from a universe of n possible elements does "
    "not by itself force a repeated element; the pigeonhole principle would "
    "require more than n selections."
)
SEARCH_SPACE = (
    "Exhaustively swept all 36 ordered pairs (A,B) of 2-element subsets of the "
    "fixed labeled universe {x_1,x_2,x_3,x_4}, with n=4 and S_1=S_k equal to "
    "that universe, in itertools.combinations lexicographic order."
)


def main():
    n = 4
    universe = tuple(range(1, n + 1))
    choices = tuple(combinations(universe, n // 2))
    first_disjoint = None
    examined = 0

    for choice_from_s1 in choices:
        for choice_from_sk in choices:
            examined += 1
            if first_disjoint is None and set(choice_from_s1).isdisjoint(choice_from_sk):
                first_disjoint = (choice_from_s1, choice_from_sk)

    assert examined == 36
    assert first_disjoint == ((1, 2), (3, 4))

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
