"""If B is known to have occurred, the conditional probability of A given B equals Pr(A ∩ B)."""

import json
from fractions import Fraction

RECORD_ID = "proofwiki_137657__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "In the uniform probability space Ω={0,1}, take A=B={0} and suppose the "
    "observed outcome is 0, so B is known to have occurred. Then Pr(A given "
    "B)=1, while Pr(A ∩ B)=1/2."
)
REFUTATION_EXPLANATION = (
    "The two exact probabilities differ: 1 is not equal to 1/2. Thus knowing "
    "that B occurred does not make the conditional probability equal to the "
    "original, unconditional probability of A ∩ B."
)
SEARCH_SPACE = (
    "Exhaustively swept all 626 triples (A,B,ω) for uniform finite spaces "
    "Ω={0,...,n-1} with 1≤n≤4, where A is any subset of Ω, B is any nonempty "
    "subset of Ω, and ω∈B represents an observed outcome for which B is known "
    "to have occurred."
)


def members(mask, n):
    return tuple(i for i in range(n) if mask & (1 << i))


def main():
    first_witness = None
    triples_checked = 0

    for n in range(1, 5):
        for a_mask in range(1 << n):
            for b_mask in range(1, 1 << n):
                intersection_size = (a_mask & b_mask).bit_count()
                conditional = Fraction(intersection_size, b_mask.bit_count())
                joint = Fraction(intersection_size, n)
                for omega in members(b_mask, n):
                    triples_checked += 1
                    if conditional != joint and first_witness is None:
                        first_witness = (
                            n,
                            members(a_mask, n),
                            members(b_mask, n),
                            omega,
                            conditional,
                            joint,
                        )

    expected = (2, (0,), (0,), 0, Fraction(1, 1), Fraction(1, 2))
    assert triples_checked == 626
    assert first_witness == expected

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
