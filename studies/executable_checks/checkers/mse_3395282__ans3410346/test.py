r"""is continuous; its image has the form $(\eta,\infty)$, since $r$ going to $0$ makes the function blow up. Take any $m \in \mathbb{N}$ with $m \ge \eta$."""

import json


def main():
    candidate_instances = ()
    witness = None
    for candidate in candidate_instances:
        witness = candidate
        break

    result = {
        "record_id": "mse_3395282__ans3410346",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No concrete witness can be formed from the supplied quote: it specifies neither the function, its domain, nor the value or definition of eta.",
        "refutation_explanation": "The supplied text is a sentence fragment and does not define the function needed to check continuity, limiting behavior, or its image. It also states no conclusion about the chosen m that could be tested. Assigning a function or eta would invent absent data.",
        "search_space": "Exhaustively swept the empty finite set of fully specified mathematical instances derivable from the quote (0 instances); no illustrative assignments were added.",
    }
    assert witness is None
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
