"""Using Euler's formula we get $$3|F|=3|E|-3|V|-6$$"""

import itertools
import json


def main():
    examined = 0
    numerical_failures = 0
    for v, e, f in itertools.product(range(13), repeat=3):
        examined += 1
        if 3 * f != 3 * e - 3 * v - 6:
            numerical_failures += 1

    assert examined == 13 ** 3
    assert numerical_failures > 0

    result = {
        "record_id": "SE_math_3992575__q",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No valid counterexample can be named because the quote does not define V, E, or F or specify which triples are admissible.",
        "refutation_explanation": "The bounded sweep finds numerical triples for which the displayed equality fails, but arbitrary triples cannot refute the claim: the supplied quote gives no domain, quantifier, object class, or hypotheses connecting V, E, and F. Consequently the search is inconclusive rather than a refutation.",
        "search_space": "Exhaustively swept all 13^3 = 2197 ordered integer triples (v, e, f) in {0,1,...,12}^3, in itertools.product order, testing 3*f == 3*e - 3*v - 6. This is only an illustrative numerical space because admissibility is unspecified."
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
