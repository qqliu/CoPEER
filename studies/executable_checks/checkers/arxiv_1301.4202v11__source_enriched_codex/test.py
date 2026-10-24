"""The inversion theorem recovers G from F without requiring the essential hypothesis α(1)≠0."""

import itertools
import json

RECORD_ID = "arxiv_1301.4202v11__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "At X=1, take alpha(1)=0. The distinct assignments G_A(1)=-1 and "
    "G_B(1)=0 both produce F(1)=alpha(1)G(1)=0."
)
REFUTATION_EXPLANATION = (
    "Because the same F(1)=0 arises from two different values of G(1), F "
    "does not determine G when alpha(1)=0. Moreover, the quoted inverse "
    "coefficient beta(1)=1/alpha(1) is undefined for this witness, so "
    "recovery cannot dispense with alpha(1) being nonzero."
)
SEARCH_SPACE = (
    "Exhaustively checked X=1 with alpha(1) in {-1,0,1} and every ordered "
    "pair of distinct values G_A(1), G_B(1) in {-1,0,1}, in fixed "
    "lexicographic order, for equal resulting F(1)."
)


def main():
    values = (-1, 0, 1)
    witness = None
    for alpha_one in values:
        for g_a, g_b in itertools.product(values, repeat=2):
            if g_a == g_b:
                continue
            f_a = alpha_one * g_a
            f_b = alpha_one * g_b
            if f_a == f_b and alpha_one == 0:
                witness = (alpha_one, g_a, g_b, f_a)
                break
        if witness is not None:
            break

    if witness != (0, -1, 0, 0):
        raise AssertionError("deterministic exhaustive search found no expected witness")

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
