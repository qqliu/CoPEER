"""For Fibonacci numbers, f_i divides f_n if and only if i divides n, without excluding the exceptional repeated initial value."""

import json

RECORD_ID = "reddit_math_3m6fzz"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "With the repeated initial Fibonacci values f_1 = f_2 = 1, the ordered "
    "pair (i, n) = (2, 1) is a counterexample: f_2 divides f_1, but 2 does "
    "not divide 1."
)
REFUTATION_EXPLANATION = (
    "The divisibility equivalence fails because 1 divides 1, so f_2 | f_1 "
    "is true, while i | n is false for i = 2 and n = 1."
)
SEARCH_SPACE = (
    "All 400 ordered pairs (i, n) with 1 <= i <= 20 and 1 <= n <= 20, "
    "using f_1 = f_2 = 1 and f_k = f_{k-1} + f_{k-2} for 3 <= k <= 20, "
    "checked in increasing i then increasing n order."
)


def fibonacci_through(limit):
    values = [0, 1, 1]
    for index in range(3, limit + 1):
        values.append(values[index - 1] + values[index - 2])
    return values


def main():
    limit = 20
    values = fibonacci_through(limit)
    witnesses = []
    for i in range(1, limit + 1):
        for n in range(1, limit + 1):
            fibonacci_divides = values[n] % values[i] == 0
            index_divides = n % i == 0
            if fibonacci_divides != index_divides:
                witnesses.append((i, n))

    if not witnesses or witnesses[0] != (2, 1):
        raise AssertionError("deterministic exhaustive sweep did not find the expected first witness")

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
