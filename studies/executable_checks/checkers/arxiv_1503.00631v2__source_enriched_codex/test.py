"""For 2.226<F≤2.26 and B=-24.116548F+54.692663, the displayed quadratic surrogate is at most 102.618907F^2-473.377198F-509.223573."""

import json
from fractions import Fraction


def decimal(value):
    return Fraction(value)


def surrogate(f_value, b_value):
    return (
        decimal("0.246345") * b_value * b_value
        + (decimal("18.810319") * f_value - decimal("42.033351")) * b_value
        + decimal("202.972148") * f_value * f_value
        - decimal("924.926294") * f_value
        + decimal("1052.803636")
    )


def asserted_bound(f_value):
    return (
        decimal("102.618907") * f_value * f_value
        - decimal("473.377198") * f_value
        - decimal("509.223573")
    )


candidates = (Fraction(9, 4),)
violations = []

for f_value in candidates:
    if decimal("2.226") < f_value <= decimal("2.26"):
        b_value = decimal("-24.116548") * f_value + decimal("54.692663")
        surrogate_value = surrogate(f_value, b_value)
        bound_value = asserted_bound(f_value)
        if surrogate_value > bound_value:
            violations.append((f_value, b_value, surrogate_value, bound_value))

if violations:
    f_value, b_value, surrogate_value, bound_value = violations[0]
    result = {
        "record_id": "arxiv_1503.00631v2__source_enriched_codex",
        "outcome": "WITNESS_FOUND",
        "witness_description": (
            "F=9/4 and B=43043/100000. The surrogate equals "
            "-1127237140734619/2000000000000000, while the asserted upper "
            "bound equals -16877024829/16000000."
        ),
        "refutation_explanation": (
            "9/4 lies in the claimed interval because 2226/1000 < 9/4 <= "
            "226/100. The exact surrogate value is greater than the asserted "
            "upper bound, so the claimed inequality fails."
        ),
        "search_space": (
            "The singleton F-space {9/4}; B is uniquely determined by the "
            "stated affine formula. This one-element finite space was swept "
            "completely in fixed tuple order using fractions.Fraction."
        ),
    }
else:
    result = {
        "record_id": "arxiv_1503.00631v2__source_enriched_codex",
        "outcome": "NO_WITNESS_EXHAUSTIVE",
        "witness_description": "No witness was found.",
        "refutation_explanation": "The sole candidate did not violate the inequality.",
        "search_space": "The singleton F-space {9/4} was swept completely.",
    }

print(json.dumps(result, separators=(",", ":")))
