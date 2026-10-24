"""Since $k$ and $k+1$ are co-prime, one of them has to be $0$ modulo $k+1$, meaning that it is a multiple of $k+1$ (and not $k+1$ itself because it's larger), so it is not prime."""

import json
from math import gcd


def is_prime(n):
    if n < 2:
        return False
    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 1
    return True


witnesses = []
for k in range(1, 101):
    modulus = k + 1
    zero_modulo_members = [n for n in (k, k + 1) if n % modulus == 0]
    if (
        gcd(k, k + 1) == 1
        and zero_modulo_members == [k + 1]
        and is_prime(k + 1)
    ):
        witnesses.append(k)

assert witnesses
assert witnesses[0] == 1

result = {
    "record_id": "SE_cs_1450__a1451",
    "outcome": "WITNESS_FOUND",
    "witness_description": "k = 1: the consecutive integers are 1 and 2, with gcd(1, 2) = 1. Of these, only 2 is 0 modulo k+1 = 2, and 2 is prime.",
    "refutation_explanation": "The member that is 0 modulo k+1 is k+1 itself, not a larger multiple. For k = 1 it is 2, which is prime, so the asserted conclusion that it is not prime is false.",
    "search_space": "All integers k from 1 through 100 inclusive, checked in increasing order using exact integer gcd, remainder, and trial-division primality tests; the full bounded space was swept.",
}
print(json.dumps(result, sort_keys=True, separators=(",", ":")))
