r"""The displayed Gaussian-integral identity evaluates the error-function argument as $-\sqrt{2}\alpha$."""

import json
from fractions import Fraction

RECORD_ID = "arxiv_1206.1893v7__source_enriched_codex"
OUTCOME = "WITNESS_FOUND"
WITNESS_DESCRIPTION = (
    "alpha = 1. The substitution x=(t-alpha)/sqrt(2) gives the "
    "error-function argument -1/sqrt(2), whereas the displayed identity "
    "uses -sqrt(2)."
)
REFUTATION_EXPLANATION = (
    "Exactly, -1/sqrt(2)=-(1/2)sqrt(2), which differs from -sqrt(2). "
    "Since erf is strictly increasing (its defining integrand is positive), "
    "the two right-hand sides differ, so alpha = 1 violates the displayed identity."
)
SEARCH_SPACE = (
    "Every alpha in the fixed ordered finite list [0, 1, -1, 2, -2] was "
    "checked exactly by comparing the rational coefficient of sqrt(2) in "
    "-alpha/sqrt(2) with the coefficient in -sqrt(2)*alpha."
)


def argument_coefficients(alpha):
    """Return exact q for arguments q*sqrt(2): (substitution, displayed)."""
    substitution_argument = Fraction(-alpha, 2)
    displayed_argument = Fraction(-alpha, 1)
    return substitution_argument, displayed_argument


def main():
    bounded_alphas = (0, 1, -1, 2, -2)
    violations = []

    for alpha in bounded_alphas:
        correct, displayed = argument_coefficients(alpha)
        if correct != displayed:
            violations.append(alpha)

    if violations != [1, -1, 2, -2]:
        raise AssertionError("exact finite sweep produced an unexpected result")

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, separators=(",", ":"), sort_keys=False))


if __name__ == "__main__":
    main()
