"""E[X!k
n ] ≈nk
k! · n−ke−kc = e−kc
k! · k!λk = λk,"""

import json


def main():
    admissible_evaluations = ()
    for _evaluation in admissible_evaluations:
        raise AssertionError("The quote licenses no evaluable instances")

    result = {
        "record_id": "Algorithms_2__sol5",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No witness can be evaluated because the supplied quote provides no admissible, fully defined instances.",
        "refutation_explanation": "The quote does not define X_n, the factorial-moment notation, n, k, c, lambda, their domains, or the meaning and limiting regime of ≈. Assigning meanings to them would invent data, so the displayed relation has no decidable counterexample predicate.",
        "search_space": "Exhaustively swept the empty finite set of admissible evaluations derivable from the quote (0 cases); no evaluation is admissible because the required definitions and domains are absent.",
    }
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
