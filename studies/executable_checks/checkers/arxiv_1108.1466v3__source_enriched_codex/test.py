"""For every prime P_k, floor(P_k+2√P_k)+1 is even and therefore cannot be prime."""

import json
from math import isqrt


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


witnesses = []
for candidate in range(2, 10001):
    if is_prime(candidate):
        value = candidate + isqrt(4 * candidate) + 1
        if value % 2 != 0:
            witnesses.append((candidate, value, is_prime(value)))

assert witnesses
assert witnesses[0] == (2, 5, True)

result = {
    "record_id": "arxiv_1108.1466v3__source_enriched_codex",
    "outcome": "WITNESS_FOUND",
    "witness_description": "P_k = 2 is prime, and floor(2 + 2√2) + 1 = 5.",
    "refutation_explanation": "Exactly, floor(2√2) = isqrt(8) = 2, so floor(2 + 2√2) + 1 = 2 + 2 + 1 = 5. This value is odd (and is itself prime), contradicting the claim that the value is even for every prime P_k.",
    "search_space": "All prime integers P_k in the inclusive range 2 through 10000, enumerated in increasing order; for each, floor(P_k + 2√P_k) + 1 was evaluated exactly as P_k + isqrt(4*P_k) + 1."
}
print(json.dumps(result, ensure_ascii=False))
