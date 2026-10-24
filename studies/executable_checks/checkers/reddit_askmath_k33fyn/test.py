"""The proof may apply the stated prime-factorization theorem to every odd integer x and obtain the displayed nonempty product of primes."""

import json


def prime_factors(n):
    """Return the conventional positive-prime factors of positive integer n."""
    factors = []
    remaining = n
    divisor = 2
    while divisor * divisor <= remaining:
        while remaining % divisor == 0:
            factors.append(divisor)
            remaining //= divisor
        divisor += 1
    if remaining > 1:
        factors.append(remaining)
    return tuple(factors)


candidates = (1,)
witness = None
for candidate in candidates:
    factors = prime_factors(candidate)
    if candidate % 2 != 0 and len(factors) == 0:
        witness = candidate
        break

if witness is not None:
    outcome = "WITNESS_FOUND"
    witness_description = "x = 1 is the concrete witness: it is odd, but its exact prime-factor tuple is empty."
    refutation_explanation = "Every prime is an integer at least 2, so a nonempty product of primes is at least 2 and cannot equal 1. Thus the displayed nonempty product cannot be obtained for the odd integer x = 1."
else:
    outcome = "NO_WITNESS_EXHAUSTIVE"
    witness_description = "No witness was found."
    refutation_explanation = "The bounded singleton search found no counterexample."

result = {
    "record_id": "reddit_askmath_k33fyn",
    "outcome": outcome,
    "witness_description": witness_description,
    "refutation_explanation": refutation_explanation,
    "search_space": "Exactly the singleton tuple (1,), traversed in that fixed order. Exact trial division checks divisors d satisfying d*d <= the remaining integer; for x = 1 there are none."
}
print(json.dumps(result, separators=(",", ":")))
