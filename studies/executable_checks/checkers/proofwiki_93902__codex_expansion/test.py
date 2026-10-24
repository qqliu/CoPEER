"""The asserted equality between the closure of H and the interior of its relative complement is false."""

import json


def main():
    candidates = ()
    for candidate in candidates:
        raise AssertionError("The explicitly empty candidate space cannot yield a candidate")

    result = {
        "record_id": "proofwiki_93902__codex_expansion",
        "outcome": "NO_WITNESS_INCONCLUSIVE",
        "witness_description": "No witness is reported because the ambient set, topology, set H, and meaning of relative complement are not specified.",
        "refutation_explanation": "The supplied quote contains only a symbolic equality. Without an ambient set, a topology, a particular H, or a specified relative complement, neither side can be evaluated and no mathematical candidate counterexample can be constructed without inventing absent data.",
        "search_space": "Exactly 0 candidates: the empty tuple of admissible instances determined by the supplied data; it is swept completely in fixed tuple order."
    }
    print(json.dumps(result, sort_keys=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
