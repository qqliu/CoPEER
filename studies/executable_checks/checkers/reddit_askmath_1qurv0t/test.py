"""Every prime number is one more or one less than a multiple of 6."""

import json


def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def main():
    violations = []
    for n in range(2, 10001):
        if is_prime(n) and n % 6 not in (1, 5):
            violations.append(n)

    if 2 not in violations:
        raise AssertionError("Expected counterexample was not found")

    result = {
        "record_id": "reddit_askmath_1qurv0t",
        "outcome": "WITNESS_FOUND",
        "witness_description": "The prime number 2 is a counterexample: 2 modulo 6 is 2, not 1 or 5.",
        "refutation_explanation": "An integer one more or one less than a multiple of 6 must have residue 1 or 5 modulo 6. Since 2 is prime and has residue 2 modulo 6, it is neither 6k+1 nor 6k-1 for any integer k, so the universal claim is false.",
        "search_space": "All integers n from 2 through 10000 inclusive, in increasing order; primality was decided by exact integer trial division, and every prime found was checked for residue 1 or 5 modulo 6."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
