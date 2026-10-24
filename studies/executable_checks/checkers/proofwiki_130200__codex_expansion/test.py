"""For n₁ > 1 with largest prime factor p, the largest prime factor of φ(n₁) is strictly less than p."""

import json


def largest_prime_factor(value):
    if value < 2:
        return None
    remaining = value
    divisor = 2
    largest = None
    while divisor * divisor <= remaining:
        while remaining % divisor == 0:
            largest = divisor
            remaining //= divisor
        divisor += 1
    if remaining > 1:
        largest = remaining
    return largest


def euler_phi(value):
    result = value
    remaining = value
    prime = 2
    while prime * prime <= remaining:
        if remaining % prime == 0:
            result -= result // prime
            while remaining % prime == 0:
                remaining //= prime
        prime += 1
    if remaining > 1:
        result -= result // remaining
    return result


violations = []
for n_1 in range(2, 101):
    p = largest_prime_factor(n_1)
    phi_value = euler_phi(n_1)
    phi_largest = largest_prime_factor(phi_value)
    if phi_largest is not None and not phi_largest < p:
        violations.append((n_1, p, phi_value, phi_largest))

assert violations
assert violations[0] == (4, 2, 2, 2)

result = {
    "record_id": "proofwiki_130200__codex_expansion",
    "outcome": "WITNESS_FOUND",
    "witness_description": "n₁ = 4, whose largest prime factor is p = 2; φ(4) = 2, whose largest prime factor is also 2.",
    "refutation_explanation": "The asserted strict inequality would require 2 < 2, which is false.",
    "search_space": "All integers n₁ with 2 ≤ n₁ ≤ 100, in increasing order; φ(n₁) and all defined largest prime factors were computed exactly."
}
print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
