"""On the circle γ of radius r centered at −ρ_k, ln|u| is constantly equal to ln r."""

import json

RECORD_ID = "proofwiki_39745__codex_expansion"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "Take r=1, ρ_k=1, and u=-2+0i. The circle is centered at -1, "
    "and u lies on it because |u-(-1)|=|-1|=1."
)
REFUTATION_EXPLANATION = (
    "For this point, |u|=2, so ln|u|=ln 2, whereas ln r=ln 1=0. "
    "Since 2≠1 and the natural logarithm is injective on positive numbers, "
    "these values are unequal."
)
SEARCH_SPACE = (
    "All 2028 tuples (r,ρ_k,x,y) with r in {1,2,3}, ρ_k in {0,1,2,3}, "
    "and x,y in {-6,-5,...,6}, checked in lexicographic loop order. "
    "Circle membership and failure of |u|=r are tested exactly using integer "
    "squared distances."
)


def main():
    first_witness = None
    tuples_checked = 0

    for r in range(1, 4):
        for rho_k in range(0, 4):
            for x in range(-6, 7):
                for y in range(-6, 7):
                    tuples_checked += 1
                    on_circle = (x + rho_k) * (x + rho_k) + y * y == r * r
                    modulus_differs = x * x + y * y != r * r
                    modulus_positive = x * x + y * y > 0
                    if (
                        first_witness is None
                        and on_circle
                        and modulus_positive
                        and modulus_differs
                    ):
                        first_witness = (r, rho_k, x, y)

    assert tuples_checked == 2028
    assert first_witness == (1, 1, -2, 0)

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
