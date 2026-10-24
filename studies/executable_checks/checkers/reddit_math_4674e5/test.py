"""The submitted proof claims that 17 is not prime."""

import json


def main():
    number = 17
    candidates = tuple(range(1, number + 1))
    divisors = tuple(d for d in candidates if number % d == 0)
    assert divisors == (1, 17)

    result = {
        "record_id": "reddit_math_4674e5",
        "outcome": "WITNESS_FOUND",
        "witness_description": "The integer 17 has exactly the positive divisors 1 and 17.",
        "refutation_explanation": "An exhaustive divisibility check finds no positive divisor of 17 other than 1 and 17. Therefore 17 is prime under the standard definition, contradicting the claim that it is not prime.",
        "search_space": "All 17 positive candidate divisors d in {1, 2, ..., 17}, checked in increasing order using 17 % d == 0.",
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
