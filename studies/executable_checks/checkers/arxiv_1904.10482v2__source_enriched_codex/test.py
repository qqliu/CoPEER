"""The displayed construction defines a low power abelian group of cardinality n."""

import json


RECORD_ID = "arxiv_1904.10482v2__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take n=12 with prime decomposition 12=2^2·3^1, indexed as p_1=2, "
    "e_1=2, p_2=3, e_2=1. The displayed construction has cardinality 6."
)
REFUTATION_EXPLANATION = (
    "Here k=2 and e_k=e_2=1, so the displayed formula gives one copy of C_2 "
    "and one copy of C_3. Their direct sum has cardinality 2·3=6, which is "
    "not n=12; therefore the displayed construction does not always define "
    "a group of cardinality n."
)
SEARCH_SPACE = (
    "All 99 integers n from 2 through 100 inclusive, each factored by "
    "deterministic trial division with prime factors indexed in increasing "
    "order. For every n, the program computes the displayed construction's "
    "cardinality as the exact integer product of p_i^e_k and sweeps the "
    "entire bounded space before selecting the first mismatch."
)


def prime_decomposition(n):
    remainder = n
    divisor = 2
    factors = []
    while divisor * divisor <= remainder:
        exponent = 0
        while remainder % divisor == 0:
            remainder //= divisor
            exponent += 1
        if exponent:
            factors.append((divisor, exponent))
        divisor += 1
    if remainder > 1:
        factors.append((remainder, 1))
    return tuple(factors)


def displayed_cardinality(factors):
    last_exponent = factors[-1][1]
    cardinality = 1
    for prime, _exponent in factors:
        cardinality *= prime ** last_exponent
    return cardinality


def main():
    mismatches = []
    swept = 0
    for n in range(2, 101):
        factors = prime_decomposition(n)
        cardinality = displayed_cardinality(factors)
        swept += 1
        if cardinality != n:
            mismatches.append((n, factors, cardinality))

    assert swept == 99
    assert mismatches
    assert mismatches[0] == (12, ((2, 2), (3, 1)), 6)

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
