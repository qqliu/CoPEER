"""For every prime P_k, floor(P_k+2√P_k)+1 is even and therefore cannot be prime."""

import json


def is_prime_exact(number):
    if number < 2:
        return False
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 1
    return True


prime = 2
radicand = 4 * prime
root = 0
while (root + 1) * (root + 1) <= radicand:
    root += 1

value = prime + root + 1
assert is_prime_exact(prime)
assert root * root <= radicand
assert radicand < (root + 1) * (root + 1)
assert value == 5
assert value % 2 == 1
assert is_prime_exact(value)

result = {
    "record_id": "arxiv_1108.1466v3__source_enriched_codex",
    "verdict": "CONFIRMED",
    "notes": "Exact integer recomputation confirms that P_k = 2 is prime and floor(2 + 2√2) + 1 = 5, which is odd and prime. The refuted universal statement is substantive, not plainly a typo."
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
