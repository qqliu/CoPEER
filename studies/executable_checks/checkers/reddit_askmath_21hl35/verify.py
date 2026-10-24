"""Every even integer a can be written as a=2n for some positive integer n."""

import json


def main():
    witness = -4
    witness_is_even = witness % 2 == 0

    # For every positive integer n, n >= 1, hence 2*n >= 2 > 0.
    # Since the witness is negative, equality with 2*n is impossible.
    positive_n_product_lower_bound = 2 * 1
    no_positive_solution = positive_n_product_lower_bound > 0 and witness < 0

    if not witness_is_even or not no_positive_solution:
        raise RuntimeError("independent exact verification failed")

    result = {
        "record_id": "reddit_askmath_21hl35",
        "verdict": "CONFIRMED",
        "notes": "Exact integer recomputation confirms that a = -4 is even, while 2n is positive for every positive integer n and therefore cannot equal -4. The refuted statement is substantive as written, not plainly a typo, though it could be repaired by restricting a to positive even integers or allowing n to be any integer."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
