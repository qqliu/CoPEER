"""Functions f,g: N→N such that g ∘ f is injective while g is not injective do not exist."""

import json

RECORD_ID = "reddit_learnmath_q0j6vm"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Let f(n)=2n. Let g(k)=k//2 when k is even, and g(k)=1 when k is odd. "
    "Then (g o f)(n)=n for every natural n, while g(1)=g(2)=1 although 1 != 2."
)
REFUTATION_EXPLANATION = (
    "The composition g o f is the identity on N and is therefore injective. "
    "The explicit collision g(1)=g(2) proves that g is not injective, so these "
    "functions contradict the claim."
)
SEARCH_SPACE = (
    "All 9 template pairs (a,c) in {1,2,3} x {1,2,3}, where f(n)=a*n and "
    "g(k)=k//a if a divides k and g(k)=c otherwise; for each pair, every "
    "ordered input pair 1 <= x < y <= 6 is checked for a collision. The entire "
    "bounded template space is swept in lexicographic order."
)


def g_value(k, a, c):
    if k % a == 0:
        return k // a
    return c


def main():
    witnesses = []
    for a in range(1, 4):
        for c in range(1, 4):
            collision = None
            for x in range(1, 7):
                for y in range(x + 1, 7):
                    if g_value(x, a, c) == g_value(y, a, c):
                        if collision is None:
                            collision = (x, y)
            if collision is not None:
                witnesses.append((a, c, collision))

    assert (2, 1, (1, 2)) in witnesses
    for n in range(1, 7):
        assert g_value(2 * n, 2, 1) == n

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, sort_keys=False))


if __name__ == "__main__":
    main()
