r"""S = \binom 02 + 19 \cdot \binom 62 + \binom 52 + 99 \cdot \binom 02 = 310."""

import json
from math import comb


def main():
    cases = ((0, 2, 19, 6, 2, 5, 2, 99, 0, 2, 310),)
    violations = []

    for n0, k0, a, n1, k1, n2, k2, b, n3, k3, rhs in cases:
        c02 = comb(n0, k0)
        c62 = comb(n1, k1)
        c52 = comb(n2, k2)
        c02_again = comb(n3, k3)
        lhs = c02 + a * c62 + c52 + b * c02_again
        if lhs != rhs:
            violations.append((c02, c62, c52, lhs, rhs))

    if violations:
        c02, c62, c52, lhs, rhs = violations[0]
        outcome = "WITNESS_FOUND"
        witness_description = (
            f"C(0,2)={c02}, C(6,2)={c62}, and C(5,2)={c52}; "
            f"therefore the left-hand side is {lhs}, not {rhs}."
        )
        refutation_explanation = (
            "Exact integer evaluation gives 0 + 19*15 + 10 + 99*0 = 295, "
            "so the asserted equality to 310 is false."
        )
    else:
        outcome = "NO_WITNESS_EXHAUSTIVE"
        witness_description = "No counterexample was found in the singleton space."
        refutation_explanation = "The displayed equality held under exact evaluation."

    payload = {
        "record_id": "mse_4124583__ans4124608",
        "outcome": outcome,
        "witness_description": witness_description,
        "refutation_explanation": refutation_explanation,
        "search_space": (
            "The singleton space consisting of the displayed closed equality, "
            "evaluated once using exact integer binomial coefficients C(0,2), "
            "C(6,2), C(5,2), and C(0,2)."
        ),
    }
    print(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
