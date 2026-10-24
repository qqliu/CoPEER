r"""Since $A^c\cap B^c$ is non-empty for each $A,B\in\mathcal F^*$, Lemma implies that any members of $\mathcal F^*$ are disjoint or one is contained in the other."""

import json

RECORD_ID = "mse_3703719__ans3707488"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = r"No source-valid witness can be identified: the quote does not define the universe, the family \mathcal F^*, or the cited Lemma and its hypotheses."
REFUTATION_EXPLANATION = r"The sweep finds the raw set-pair U={0,1,2,3}, A={0,1}, B={0,2}: U\(A∪B)={3}, while A∩B={0} and neither set contains the other. This only refutes the premise-to-conclusion implication for unrestricted ordinary subsets; the quote gives no way to decide whether these sets belong to \mathcal F^* or satisfy the omitted Lemma's hypotheses, so it is not a counterexample to the sourced claim."
SEARCH_SPACE = r"Exhaustively swept the 341 ordered pairs (A,B) of subsets of each canonical universe U_n={0,...,n-1} for n=0,1,2,3,4 (sum_{n=0}^4 4^n=341), testing exactly whether U_n\(A∪B) is nonempty and whether A,B are disjoint or nested. No membership or Lemma-hypothesis filter was possible from the quote."


def main():
    swept = 0
    first_raw_candidate = None

    for n in range(5):
        subset_count = 1 << n
        universe_mask = subset_count - 1
        for a_mask in range(subset_count):
            for b_mask in range(subset_count):
                swept += 1
                common_complement_nonempty = (
                    universe_mask & ~(a_mask | b_mask)
                ) != 0
                disjoint = (a_mask & b_mask) == 0
                a_contained_in_b = (a_mask & b_mask) == a_mask
                b_contained_in_a = (a_mask & b_mask) == b_mask
                conclusion = disjoint or a_contained_in_b or b_contained_in_a
                if common_complement_nonempty and not conclusion:
                    if first_raw_candidate is None:
                        first_raw_candidate = (n, a_mask, b_mask)

    assert swept == 341
    assert first_raw_candidate == (4, 3, 5)

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
