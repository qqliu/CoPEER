r"""**Lemma**: let $m,n \in \mathbb{N}$. Then, the set $\{2,...,m\}$ contains (at least) as many multiples of $n$ as $\{m+2, ..., 2m\}$."""

import json


def count_multiples(start, stop, divisor):
    return sum(1 for value in range(start, stop + 1) if value % divisor == 0)


def main():
    witnesses = []
    for m in range(1, 17):
        for n in range(1, 17):
            left_count = count_multiples(2, m, n)
            right_count = count_multiples(m + 2, 2 * m, n)
            if left_count < right_count:
                witnesses.append((m, n, left_count, right_count))

    if not witnesses or witnesses[0] != (2, 4, 0, 1):
        raise AssertionError("deterministic bounded search did not find the expected first witness")

    result = {
        "record_id": "SE_math_4537650__q",
        "outcome": "WITNESS_FOUND",
        "witness_description": "m = 2 and n = 4. The set {2,...,m} is {2}, while {m+2,...,2m} is {4}.",
        "refutation_explanation": "The left set contains 0 multiples of 4, whereas the right set contains 1 multiple of 4 (namely 4), so the left set does not contain at least as many multiples as the right set.",
        "search_space": "All 256 ordered pairs (m,n) with 1 <= m <= 16 and 1 <= n <= 16 were checked in lexicographic order, using the literal inclusive integer ranges {2,...,m} and {m+2,...,2m}."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
