r"""However, one can show that $$\sum \limits_{i=1}^{r}\left(\frac{5n}{2}-3i\right)-3r+ \left\lfloor \frac{(n-3r)^2}{4}\right\rfloor\leq \left\lfloor \frac{n^2}{4}\right\rfloor,$$"""

import itertools
import json
from fractions import Fraction


def floor_fraction(value):
    return value.numerator // value.denominator


def sides(n, r):
    series = sum(
        (Fraction(5 * n, 2) - 3 * i for i in range(1, r + 1)),
        Fraction(0, 1),
    )
    lhs = series - 3 * r + floor_fraction(Fraction((n - 3 * r) ** 2, 4))
    rhs = (n ** 2) // 4
    return lhs, rhs


def main():
    violations = []
    for r, n in itertools.product(range(1, 21), range(1, 21)):
        lhs, rhs = sides(n, r)
        if lhs > rhs:
            violations.append((n, r, lhs, rhs))

    witness = violations[0]
    assert witness == (5, 1, Fraction(15, 2), 6)

    result = {
        "record_id": "mse_4515175__ans4515778",
        "outcome": "WITNESS_FOUND",
        "witness_description": "For positive integers n=5 and r=1, the left-hand side is 15/2 while the right-hand side is 6.",
        "refutation_explanation": "The displayed inequality evaluates to 15/2 <= 6, which is false.",
        "search_space": "All 400 positive-integer pairs (n, r) with 1 <= n <= 20 and 1 <= r <= 20, iterated in increasing r and then increasing n; every pair was evaluated exactly.",
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
