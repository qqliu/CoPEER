r"""For every integer n ≥ 1, the sum of the squares from 1 through n equals n(n+1)(n+2)/6."""

import json


def main():
    n = 2
    left = 0
    k = 1
    while k <= n:
        left += k * k
        k += 1

    numerator = n * (n + 1) * (n + 2)
    right, remainder = divmod(numerator, 6)
    established = n >= 1 and left == 5 and remainder == 0 and right == 4 and left != right

    verdict = "CONFIRMED" if established else "CANNOT_REPRODUCE"
    notes = (
        "Exact recomputation at n = 2 gives a sum of squares of 5 and a right-hand side of 4, "
        "so the universal claim is false. The refuted statement is plainly a typo: the standard "
        "numerator factor is 2n+1, not n+2."
    )
    result = {
        "record_id": "reddit_learnmath_fnlluu",
        "verdict": verdict,
        "notes": notes,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
