"""For every prime p, (2^(p-1))(2^p-1) is a perfect number."""

import json
from math import isqrt


def is_prime(n):
    if n < 2:
        return False
    for divisor in range(2, isqrt(n) + 1):
        if n % divisor == 0:
            return False
    return True


def proper_divisor_sum(n):
    if n == 1:
        return 0
    total = 1
    for divisor in range(2, isqrt(n) + 1):
        if n % divisor == 0:
            total += divisor
            partner = n // divisor
            if partner != divisor:
                total += partner
    return total


witnesses = []
for p in range(2, 12):
    if is_prime(p):
        number = (2 ** (p - 1)) * ((2 ** p) - 1)
        divisor_sum = proper_divisor_sum(number)
        if divisor_sum != number:
            witnesses.append((p, number, divisor_sum))

assert witnesses
assert witnesses[0] == (11, 2096128, 2325392)

result = {
    "record_id": "reddit_mathematics_1bl4g2p",
    "outcome": "WITNESS_FOUND",
    "witness_description": "p=11, which is prime, gives N=(2^10)(2^11-1)=2096128; the sum of N's proper positive divisors is 2325392, not 2096128.",
    "refutation_explanation": "The claim is universal over primes. The exact bounded search finds the prime p=11, for which the constructed number is not perfect because its proper-divisor sum differs from the number. This single witness refutes the claim.",
    "search_space": "Every integer p from 2 through 11 inclusive was tested for primality in increasing order. For each prime p in (2, 3, 5, 7, 11), N=(2^(p-1))(2^p-1) was formed exactly and every possible divisor d from 2 through floor(sqrt(N)) was checked to compute the complete proper-divisor sum."
}
print(json.dumps(result, separators=(",", ":")))
