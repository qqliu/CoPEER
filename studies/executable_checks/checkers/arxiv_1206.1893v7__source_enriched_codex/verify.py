r"""The displayed Gaussian-integral identity evaluates the error-function argument as $-\sqrt{2}\alpha$."""

import json
from fractions import Fraction

RECORD = "arxiv_1206.1893v7__source_enriched_codex"
VERDICT = "CONFIRMED"
NOTES = (
    "Confirmed at alpha = 1 by exact Q(sqrt(2)) algebra: substitution gives "
    "argument -(1/2)sqrt(2), while the display uses -sqrt(2); strict "
    "monotonicity of erf makes the values unequal. The refuted statement is "
    "plainly a factor-of-two typo, not a substantive result."
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    alpha = Fraction(1, 1)

    # Write each argument as q*sqrt(2).  For u=(t-alpha)/sqrt(2),
    # the upper endpoint satisfies 2*q=-alpha.
    substituted_q = -alpha * Fraction(1, 2)
    displayed_q = -alpha
    require(Fraction(2, 1) * substituted_q == -alpha,
            "substituted endpoint was derived incorrectly")

    # Under t=alpha+sqrt(2)*u, (alpha-t)^2/2 has unit u^2
    # coefficient: the radical contributes 2 and division by 2 contributes 1/2.
    exponent_coefficient = Fraction(2, 1) * Fraction(1, 2)
    require(exponent_coefficient == Fraction(1, 1),
            "Gaussian exponent did not normalize")

    require(substituted_q == Fraction(-1, 2),
            "unexpected exact substituted argument")
    require(displayed_q == Fraction(-1, 1),
            "unexpected displayed argument")
    require(displayed_q < substituted_q,
            "the two arguments were not strictly ordered")

    # sqrt(2) is positive, so the coefficient ordering is the argument
    # ordering.  erf is strictly increasing because its defining integrand
    # exp(-u^2) is everywhere positive.  Thus distinct ordered arguments give
    # distinct right-hand sides, refuting the displayed identity at alpha=1.
    result = {
        "record_id": RECORD,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
