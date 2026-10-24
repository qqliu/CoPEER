"""If bi > 0, the maximum of yTx subject to aT
i x ≤bi is yT ai
bi
(achieved at x = ai
bi ), so we
must have yT ai
bi
≤1, i.e., yTai ≤bi."""

import json
from fractions import Fraction

RECORD_ID = "Algorithms_43__sol5"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = "In scalar dimension, take ai = 1, bi = 2, y = 1, and x = 2. Then bi > 0 and ai*x = 2 <= bi, while y*x = 2 is greater than the claimed maximum y*ai/bi = 1/2."
REFUTATION_EXPLANATION = "For these values the feasible set is x <= 2 and the objective is x, whose maximum is 2 at x = 2. The claim instead gives 1/2, allegedly achieved at x = 1/2, so its stated maximum is false."
SEARCH_SPACE = "Exhaustively swept all 10 scalar tuples with ai = 1, y = 1, bi in (1, 2), and integer candidate x in (-2, -1, 0, 1, 2), in that fixed nested-loop order; every comparison used Fraction exact arithmetic."


def main():
    violations = []
    for ai in (1,):
        for y in (1,):
            for bi in (1, 2):
                claimed_maximum = Fraction(y * ai, bi)
                for x in (-2, -1, 0, 1, 2):
                    feasible = ai * x <= bi
                    objective = Fraction(y * x, 1)
                    if bi > 0 and feasible and objective > claimed_maximum:
                        violations.append((objective, ai, bi, y, x))

    assert len(violations) > 0
    witness = max(violations)
    assert witness == (Fraction(2, 1), 1, 2, 1, 2)

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
