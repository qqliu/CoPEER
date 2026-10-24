"""Say that after first pass $x_0$ switches place with $x_m$, so the final array $B$ starts with the entry $x_m$ regardless of the position of $x_0$ (which can further switch place with $x_{2m}$ and so on). Thus, $x_m < x_0$."""

import json
from itertools import product


def main():
    domain = tuple(range(-2, 3))
    non_less_pairs = []
    examined = 0

    for x_0, x_m in product(domain, repeat=2):
        examined += 1
        if not (x_m < x_0):
            non_less_pairs.append((x_0, x_m))

    assert examined == 25
    assert len(non_less_pairs) == 15

    result = {
        "record_id": "SE_cs_81391__q",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No certified witness: the bounded sweep finds integer pairs with x_m not less than x_0, but the quote gives no rule for deciding whether any such pair can undergo the stated first-pass switch.",
        "refutation_explanation": "The source does not define the first pass, the condition causing entries to switch places, or any assumption connecting that switch to the values' order. Therefore the admissibility of candidate counterexamples cannot be checked without inventing missing definitions.",
        "search_space": "All 25 ordered pairs (x_0, x_m) in {-2,-1,0,1,2}^2, in itertools.product order; the predicate x_m < x_0 was evaluated exactly for every pair. The sweep found 15 non-less pairs, but the quote supplies no predicate deciding which pairs can undergo the stated first-pass switch."
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
