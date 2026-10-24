"""In any imaginary quadratic number field, if a unit is congruent to 1 modulo a prime ideal above a rational prime p≥3, then the unit equals 1."""

import json

RECORD_ID = "arxiv_0901.4305v5__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "K = Q(√-3), O_K = Z[ω] with ω²+ω+1=0; p=3; "
    "wp=(1-ω); ε=ω."
)
REFUTATION_EXPLANATION = (
    "N(ω)=1, so ω is a unit, and ω≠1. Since ω-1=-(1-ω) lies in wp, "
    "ω≡1 modulo wp. Multiplication by 1-ω has determinant 3, and "
    "3=(1-ω)(2+ω), so wp has index 3 and is a prime ideal above 3. "
    "Thus this ε violates the claim."
)
SEARCH_SPACE = (
    "All 25 Eisenstein integers ε=a+bω with integers -2≤a≤2 and "
    "-2≤b≤2, in fixed lexicographic order, tested for unit norm and "
    "congruence to 1 for the single pair p=3, wp=(1-ω) in Z[ω]."
)


def multiply(x, y):
    """Multiply pairs representing a+bω, using ω²=-ω-1."""
    a, b = x
    c, d = y
    return (a * c - b * d, a * d + b * c - b * d)


def norm(x):
    """Exact field norm of a+bω."""
    a, b = x
    return a * a - a * b + b * b


def in_wp(x):
    """Test membership in (1-ω); equivalently a+b is divisible by 3."""
    a, b = x
    return (a + b) % 3 == 0


def main():
    generator = (1, -1)

    # The multiplication matrix of 1-ω has columns (1,-1) and (1,2).
    determinant = 1 * 2 - 1 * (-1)
    assert determinant == 3
    assert multiply(generator, (2, 1)) == (3, 0)

    witnesses = []
    for a in range(-2, 3):
        for b in range(-2, 3):
            epsilon = (a, b)
            difference = (a - 1, b)
            if norm(epsilon) == 1 and epsilon != (1, 0) and in_wp(difference):
                witnesses.append(epsilon)

    assert (0, 1) in witnesses

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
