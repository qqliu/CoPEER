"""For odd n with floor(n/2) even, (floor(n/2)+1)*2 equals n+2."""

import json


def main():
    first_witness = None

    for n in range(1, 102):
        half_floor = n // 2
        admissible = n % 2 == 1 and half_floor % 2 == 0
        left = (half_floor + 1) * 2
        right = n + 2
        if admissible and left != right and first_witness is None:
            first_witness = (n, half_floor, left, right)

    if first_witness != (1, 0, 2, 3):
        raise RuntimeError("deterministic bounded search did not find the expected witness")

    result = {
        "record_id": "reddit_learnmath_8yjpp7",
        "outcome": "WITNESS_FOUND",
        "witness_description": "n = 1: it is odd, floor(1/2) = 0 is even, but (0+1)*2 = 2 whereas 1+2 = 3.",
        "refutation_explanation": "The two sides are unequal (2 != 3), so n = 1 satisfies the hypotheses and falsifies the universal equality.",
        "search_space": "All integers n from 1 through 101 inclusive, tested in increasing order; admissible n are those with n odd and floor(n/2) even."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
