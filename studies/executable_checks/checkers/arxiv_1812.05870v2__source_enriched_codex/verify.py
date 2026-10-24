r"""For the stated CDF and prices tending to 1, inequality (20) holds for all n>1: (F_n)^n is at least (c+1)^{n-1}(\tau_n)^{n-1}((c+1)\tau_n-c(\tau_n)^2)."""

import json
from fractions import Fraction

RECORD_ID = "arxiv_1812.05870v2__source_enriched_codex"
VERDICT = "CONFIRMED"
NOTES = ("The witness is valid. Exact rational recomputation gives tau_2=1/2, "
         "F(tau_2)=3/4, LHS=9/16, and RHS=3/4, so the claimed "
         "greater-than-or-equal inequality fails. The sequence has "
         "1-tau_m=1/m and therefore tends to 1. The refuted statement is "
         "substantive, not plainly a typo: the displayed relation is "
         "systematically in the opposite direction for this nondegenerate case.")


def repeated_product(value, count):
    assert isinstance(count, int) and count >= 0
    result = Fraction(1, 1)
    for _ in range(count):
        result *= value
    return result


def price(index):
    assert isinstance(index, int) and index >= 1
    return Fraction(index - 1, index)


def convergence_cutoff(epsilon):
    assert isinstance(epsilon, Fraction) and epsilon > 0
    cutoff = max(2, epsilon.denominator // epsilon.numerator + 1)
    assert Fraction(1, cutoff) < epsilon
    assert Fraction(1, 1) - price(cutoff) == Fraction(1, cutoff)
    return cutoff


def main():
    # This constructs an exact epsilon cutoff for several arbitrary rational
    # inputs; the same integer formula works for every positive rational input.
    for epsilon in (Fraction(1, 2), Fraction(1, 7), Fraction(3, 101)):
        cutoff = convergence_cutoff(epsilon)
        assert Fraction(1, 1) - price(cutoff) < epsilon

    c = 1
    n = 2
    tau = price(n)

    # For c=1, the stated CDF is F(x)=2x-x*x.
    f_value = Fraction(c + 1, 1) * tau - Fraction(c, 1) * tau * tau
    lhs = repeated_product(f_value, n)
    rhs = (repeated_product(Fraction(c + 1, 1), n - 1)
           * repeated_product(tau, n - 1)
           * f_value)

    assert n > 1
    assert tau == Fraction(1, 2)
    assert f_value == Fraction(3, 4)
    assert lhs == Fraction(9, 16)
    assert rhs == Fraction(3, 4)
    assert lhs < rhs

    result = {
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "notes": NOTES,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
