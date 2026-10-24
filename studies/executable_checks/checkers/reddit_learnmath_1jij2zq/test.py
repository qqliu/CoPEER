"""For general n, x+y equals the displayed sum from i=0 to 1 with binomial coefficients depending on n."""

import json
from math import comb


def displayed_sum(n, x, y):
    return sum(comb(n, i) * (x ** i) * (y ** (n - i)) for i in range(2))


def main():
    counterexamples = []
    examined = 0

    for n in range(1, 7):
        for x in range(1, 6):
            for y in range(1, 6):
                examined += 1
                left = x + y
                right = displayed_sum(n, x, y)
                if left != right:
                    counterexamples.append((n, x, y, left, right))

    assert examined == 150
    assert counterexamples
    assert counterexamples[0] == (2, 1, 1, 2, 3)

    result = {
        "record_id": "reddit_learnmath_1jij2zq",
        "outcome": "WITNESS_FOUND",
        "witness_description": "(n, x, y) = (2, 1, 1).",
        "refutation_explanation": "At n=2, x=1, y=1, the left side is x+y=2, while the displayed sum is C(2,0)*1^0*1^2 + C(2,1)*1^1*1^1 = 1+2 = 3. Since 2 != 3, this instance refutes the claimed general equality.",
        "search_space": "All 150 triples (n, x, y) with n in {1,2,3,4,5,6} and x,y in {1,2,3,4,5}, in lexicographic order."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
