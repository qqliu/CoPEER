"""For an arbitrary fixed natural number k, P(1) and P(k) suffice to imply P(k+1)."""

import json


def holds(mask, n):
    if n < 1 or n > 3:
        return False
    return bool(mask & (1 << (n - 1)))


def main():
    k = 2
    violations = []
    for mask in range(1 << 3):
        if holds(mask, 1) and holds(mask, k) and not holds(mask, k + 1):
            subset = tuple(n for n in range(1, 4) if holds(mask, n))
            violations.append((mask, subset))

    assert violations == [(3, (1, 2))]

    result = {
        "record_id": "reddit_math_5wlvhh",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Take k = 2 and define P(n) to hold exactly when n is in {1, 2}. Then P(1) and P(2) hold, while P(3) does not.",
        "refutation_explanation": "For this predicate and k = 2, both hypotheses P(1) and P(k) are true, but the claimed conclusion P(k+1) = P(3) is false.",
        "search_space": "All 8 predicates P_S on the natural numbers defined by P_S(n) iff n belongs to S, where S ranges over every subset of {1, 2, 3}, with the fixed value k = 2; all 8 predicates are swept in mask order 0 through 7."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
