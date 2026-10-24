r"""Suppose not, then $$e(G)\le e(X)+e(X,V(G)-X)+e(V(G)-X)$$ $$\le \frac{1}{4}\left(\frac{3}{4}n-C_1\right)^2+\left(\frac{3}{4}n-C_1\right)\left(\frac{1}{4}n+C_1\right)+\frac{3}{8}\left(\frac{1}{4}n+C_1\right)^2$$"""

import json
from fractions import Fraction
from itertools import product

RECORD_ID = "mse_4935900__ans4936134"
OUTCOME = "NO_WITNESS_INCONCLUSIVE"
WITNESS_DESCRIPTION = "No counterexample can be certified from the supplied claim."
REFUTATION_EXPLANATION = (
    "The quote does not state what “Suppose not” negates and gives no definitions, "
    "domains, or constraints for G, X, e(G), e(X), e(X,V(G)-X), "
    "e(V(G)-X), n, or C_1. Although the displayed arithmetic right-hand side "
    "can be evaluated for chosen n and C_1, neither inequality can be tested "
    "without inventing absent graph-theoretic data."
)
SEARCH_SPACE = (
    "Illustrative exact sweep of all 4,225 ordered integer pairs (n,C_1) in "
    "{-32,-31,...,32}^2. The displayed arithmetic right-hand side was evaluated "
    "exactly for every pair, but no graph or edge-count candidate was testable; "
    "this sweep is not exhaustive evidence for or against the claim."
)


def arithmetic_rhs(n, c_one):
    n_exact = Fraction(n, 1)
    c_exact = Fraction(c_one, 1)
    left_size = Fraction(3, 4) * n_exact - c_exact
    right_size = Fraction(1, 4) * n_exact + c_exact
    return (
        Fraction(1, 4) * left_size * left_size
        + left_size * right_size
        + Fraction(3, 8) * right_size * right_size
    )


def main():
    evaluated = []
    values = range(-32, 33)
    for n, c_one in product(values, values):
        evaluated.append((n, c_one, arithmetic_rhs(n, c_one)))
    assert len(evaluated) == 4225

    result = {
        "record_id": RECORD_ID,
        "outcome": OUTCOME,
        "witness_description": WITNESS_DESCRIPTION,
        "refutation_explanation": REFUTATION_EXPLANATION,
        "search_space": SEARCH_SPACE,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=False))


if __name__ == "__main__":
    main()
