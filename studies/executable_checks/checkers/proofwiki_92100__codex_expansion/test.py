"""The proof claims that tan(x/2) ≠ 0 implies, for every integer n, 2πn < x < 2πn + π."""

import json
from fractions import Fraction


def main():
    candidates = ((Fraction(1, 2), Fraction(1, 1)),)
    integers = (0, 1)
    witness = None

    for x_coefficient, exact_tangent in candidates:
        premise = exact_tangent != 0
        failures = []
        for n in integers:
            lower_coefficient = 2 * n
            upper_coefficient = 2 * n + 1
            conclusion = lower_coefficient < x_coefficient < upper_coefficient
            if not conclusion:
                failures.append(n)
        if premise and failures:
            witness = (x_coefficient, failures[0])
            break

    if witness != (Fraction(1, 2), 1):
        raise AssertionError("expected counterexample was not found")

    result = {
        "record_id": "proofwiki_92100__codex_expansion",
        "outcome": "WITNESS_FOUND",
        "witness_description": "x = π/2 is a witness: tan(x/2) = tan(π/4) = 1 ≠ 0, but the asserted inequality fails for n = 1.",
        "refutation_explanation": "For n = 1 the conclusion requires 2π < π/2 < 3π. Since π > 0, the first inequality 2π < π/2 is false, so the claimed implication is false.",
        "search_space": "Exhaustively swept x ∈ {π/2} and n ∈ {0, 1}, representing multiples of positive π by Fraction coefficients and using the exact identity tan(π/4) = 1."
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
