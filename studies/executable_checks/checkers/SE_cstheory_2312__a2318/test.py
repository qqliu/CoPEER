r"""We started with a graph whose edge weights had sum $T$, and added $f$ to the sum of the edge weights. Since $-.99T \leq f \leq -.49T$, we're O.K."""

import json
from fractions import Fraction
from itertools import product


def main():
    values = range(-100, 101)
    examined = 0
    admissible = 0

    for total, added in product(values, repeat=2):
        examined += 1
        lower = Fraction(-99, 100) * total
        upper = Fraction(-49, 100) * total
        if lower <= added <= upper:
            admissible += 1
            # The quote supplies no predicate corresponding to “we're O.K.”,
            # so even an admissible pair cannot be judged a counterexample.

    assert examined == 40401
    assert admissible >= 0

    result = {
        "record_id": "SE_cstheory_2312__a2318",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness is identifiable because the supplied text never defines what “we're O.K.” means.",
        "refutation_explanation": "The bounded sweep can decide exactly which integer pairs satisfy the stated inequalities, but the claimed conclusion is an undefined predicate. Therefore no pair can be classified as a counterexample from the supplied data alone.",
        "search_space": "All 40,401 ordered integer pairs (T, f) in {-100, -99, ..., 100}^2, in lexicographic product order; each pair was exactly classified by whether (-99/100)T <= f <= (-49/100)T. This finite sweep does not exhaust graphs or interpretations of “we're O.K.”, neither of which the quote defines."
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
