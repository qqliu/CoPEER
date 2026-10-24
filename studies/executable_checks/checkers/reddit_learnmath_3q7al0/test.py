"""The submitted proof claims that 2/3 + 1 = 1."""

import json
from fractions import Fraction


def main():
    equations = ((Fraction(2, 3), Fraction(1, 1), Fraction(1, 1)),)
    witness_found = False
    for left_term, added_term, asserted_result in equations:
        if left_term + added_term != asserted_result:
            witness_found = True
            break

    if not witness_found:
        raise AssertionError("The singleton search was expected to find a witness")

    result = {
        "record_id": "reddit_learnmath_3q7al0",
        "outcome": "WITNESS_FOUND",
        "witness_description": "For the sole supplied equation, Fraction(2, 3) + Fraction(1, 1) equals Fraction(5, 3), not Fraction(1, 1).",
        "refutation_explanation": "Exact rational arithmetic gives 2/3 + 1 = 5/3; since 5/3 is not 1, the submitted equality is false.",
        "search_space": "The singleton space containing exactly the supplied asserted equation (2/3 + 1 = 1) was exhaustively checked using fractions.Fraction.",
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
