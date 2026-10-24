r"""(this can be done in $\dbinom{u}{m}$ ways)"""

import itertools
import json
import math

RECORD_ID = "mse_1277263__ans1278144"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = (
    "No counterexample can be identified because the quote does not define "
    "what “this” denotes or quantify u and m."
)
REFUTATION_EXPLANATION = (
    "The bounded sweep exactly verifies that, for every integer pair "
    "0 <= m <= u <= 8, the number of enumerated m-element subsets of "
    "range(u) equals math.comb(u, m). This checks only the binomial "
    "expression; it cannot test the quoted counting claim because the "
    "objects or operation referred to by “this” are absent."
)
SEARCH_SPACE = (
    "All 45 integer pairs (u, m) with 0 <= m <= u <= 8, and every "
    "m-element subset of range(u) for each pair."
)


def main():
    checked_pairs = 0
    for u in range(9):
        for m in range(u + 1):
            enumerated = sum(1 for _ in itertools.combinations(range(u), m))
            assert enumerated == math.comb(u, m)
            checked_pairs += 1
    assert checked_pairs == 45

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
