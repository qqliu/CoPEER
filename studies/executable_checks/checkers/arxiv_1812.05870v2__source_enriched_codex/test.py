r"""For the stated CDF and prices tending to 1, inequality (20) holds for all n>1: (F_n)^n is at least (c+1)^{n-1}(\tau_n)^{n-1}((c+1)\tau_n-c(\tau_n)^2)."""

import json
from fractions import Fraction


def price(m, k):
    return Fraction(m + k - 1, m + k)


def main():
    violations = []
    tested = 0

    for c in (0, 1):
        for k in range(4):
            for n in range(2, 9):
                tested += 1
                tau = price(n, k)
                f_value = (c + 1) * tau - c * tau ** 2
                lhs = f_value ** n
                rhs = ((c + 1) ** (n - 1) * tau ** (n - 1)
                       * ((c + 1) * tau - c * tau ** 2))
                assert Fraction(0, 1) < tau < Fraction(1, 1)
                assert Fraction(0, 1) <= f_value <= Fraction(1, 1)
                if lhs < rhs:
                    violations.append((c, k, n, tau, f_value, lhs, rhs))

    assert tested == 56
    assert violations
    assert violations[0] == (
        1, 0, 2, Fraction(1, 2), Fraction(3, 4),
        Fraction(9, 16), Fraction(3, 4)
    )

    result = {
        "record_id": "arxiv_1812.05870v2__source_enriched_codex",
        "outcome": "WITNESS_FOUND",
        "witness_description": "Take c=1 and the price sequence tau_m=(m-1)/m for every integer m>=2. This sequence tends to 1, and at n=2 it has tau_2=1/2.",
        "refutation_explanation": "With c=1, n=2, and tau_2=1/2, F(tau_2)=2(1/2)-(1/2)^2=3/4. Thus (F_2)^2=9/16, while the claimed lower bound is 2(1/2)(3/4)=3/4=12/16, so 9/16 is not at least 12/16.",
        "search_space": "All 56 triples (c,k,n) in {0,1} x {0,1,2,3} x {2,3,4,5,6,7,8}, using the exact convergent price sequences tau_m=(m+k-1)/(m+k); every triple was evaluated with Fraction arithmetic."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
