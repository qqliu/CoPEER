"""For positive s_i, the proof claims that the derivative with respect to r of (Σ_i s_i^r)^(1/r) equals 0 at r=1."""

import itertools
import json

RECORD_ID = "proofwiki_3078__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "Positive tuple (s_1, s_2) = (1, 1); at r = 1 its derivative is -2*log(2), which is nonzero."
REFUTATION_EXPLANATION = "For this tuple, (Σ_i s_i^r)^(1/r) = 2^(1/r). Exact symbolic differentiation gives derivative -2*log(2) at r=1. Since 2>1, log(2) is nonzero, contradicting the claimed value 0."
SEARCH_SPACE = "All 84 ordered tuples of positive integers with length 1, 2, or 3 and each entry in {1,2,3,4}, in increasing length and lexicographic order; the full space was swept."


def prime_exponents(value):
    """Return the exact prime-exponent dictionary of a positive integer."""
    exponents = {}
    remaining = value
    prime = 2
    while prime * prime <= remaining:
        exponent = 0
        while remaining % prime == 0:
            remaining //= prime
            exponent += 1
        if exponent:
            exponents[prime] = exponent
        prime += 1
    if remaining > 1:
        exponents[remaining] = exponents.get(remaining, 0) + 1
    return exponents


def derivative_log_coefficients(values):
    """Compute exact coefficients in f'(1)=sum_p c_p*log(p)."""
    total = sum(values)
    coefficients = {}
    for value in values:
        for prime, exponent in prime_exponents(value).items():
            coefficients[prime] = coefficients.get(prime, 0) + value * exponent
    for prime, exponent in prime_exponents(total).items():
        coefficients[prime] = coefficients.get(prime, 0) - total * exponent
    return {prime: coefficient for prime, coefficient in coefficients.items() if coefficient != 0}


first_witness = None
checked = 0
for length in range(1, 4):
    for values in itertools.product(range(1, 5), repeat=length):
        checked += 1
        coefficients = derivative_log_coefficients(values)
        if coefficients and first_witness is None:
            first_witness = (values, coefficients)

assert checked == 84
assert first_witness == ((1, 1), {2: -2})

result = {
    "record_id": RECORD_ID,
    "outcome": OUTCOME,
    "witness_description": WITNESS_DESCRIPTION,
    "refutation_explanation": REFUTATION_EXPLANATION,
    "search_space": SEARCH_SPACE,
}
print(json.dumps(result, separators=(",", ":")))
