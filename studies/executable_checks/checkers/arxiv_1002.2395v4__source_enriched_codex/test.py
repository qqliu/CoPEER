"""Every real-valued function F on the subsets of <n> with F(φ)=1 that satisfies F(α∩β)F(α∪β)≤F(α)F(β) for all α,β⊆<n> also satisfies (S_k^F)^2≥|S_{k-1}^F S_{k+1}^F| for 1≤k<n."""

import itertools
import json


def satisfies_premise(values, n):
    subset_count = 1 << n
    for alpha in range(subset_count):
        for beta in range(subset_count):
            intersection = alpha & beta
            union = alpha | beta
            if values[intersection] * values[union] > values[alpha] * values[beta]:
                return False
    return True


def main():
    value_choices = (-1, 0, 1)
    swept = 0
    admissible = 0
    for n in (1, 2, 3):
        nonempty_count = (1 << n) - 1
        for assigned in itertools.product(value_choices, repeat=nonempty_count):
            values = (1,) + assigned
            swept += 1
            if satisfies_premise(values, n):
                admissible += 1

    assert swept == 2217
    assert admissible >= 0

    result = {
        "record_id": "arxiv_1002.2395v4__source_enriched_codex",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness can be certified because neither target_claim nor source_quote defines S_k^F.",
        "refutation_explanation": "The bounded sweep can decide the Hadamard-Fischer premise for each candidate F, but the claimed conclusion cannot be evaluated without a definition of S_k^F. The result is therefore inconclusive and is not evidence that the claim holds over all real-valued functions.",
        "search_space": "All 2,217 functions F for n in {1,2,3} taking values in {-1,0,1} on nonempty subsets and satisfying F(empty)=1 were enumerated in fixed order; every ordered pair of subsets was checked for the Hadamard-Fischer premise. This is exhaustive only for that finite diagnostic space, not for arbitrary real-valued F or arbitrary n."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
