"""The displayed construction defines a low power abelian group of cardinality n."""

import json

RECORD_ID = "arxiv_1904.10482v2__source_enriched_codex"
NOTES = (
    "Exact recomputation gives 12 = 2^2 * 3^1, while the displayed use of "
    "e_k = 1 produces C_2 direct-sum C_3, of cardinality 2 * 3 = 6, not "
    "12. The refuted statement is plainly a typo: the inner bound should be "
    "e_i rather than e_k."
)


def factor_exact(value):
    remaining = value
    candidate = 2
    result = []
    while candidate * candidate <= remaining:
        multiplicity = 0
        while remaining % candidate == 0:
            remaining //= candidate
            multiplicity += 1
        if multiplicity != 0:
            result.append((candidate, multiplicity))
        candidate += 1
    if remaining != 1:
        result.append((remaining, 1))
    return tuple(result)


def multiply_prime_powers(decomposition):
    value = 1
    for prime, exponent in decomposition:
        for unused in range(exponent):
            value *= prime
    return value


def order_of_displayed_group(decomposition):
    common_multiplicity = decomposition[-1][1]
    order = 1
    for prime, unused_exponent in decomposition:
        for unused in range(common_multiplicity):
            order *= prime
    return order


def main():
    claimed_n = 12
    decomposition = factor_exact(claimed_n)
    reconstructed_n = multiply_prime_powers(decomposition)
    displayed_order = order_of_displayed_group(decomposition)

    witness_is_valid = (
        decomposition == ((2, 2), (3, 1))
        and reconstructed_n == claimed_n
        and displayed_order == 6
        and displayed_order != claimed_n
    )
    verdict = "CONFIRMED" if witness_is_valid else "REFUTED_WITNESS_INVALID"
    result = {
        "record_id": RECORD_ID,
        "verdict": verdict,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
